# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
import json
from users.models import FCMToken
from pyfcm import FCMNotification
from django.conf import settings
from users.models import Profile


# Push notification function
def send_push_notification(user, title, message, data):
    push_service = FCMNotification(api_key=settings.FCM_SERVER_KEY)
    try:
        token = FCMToken.objects.get(user=user).token
    except FCMToken.DoesNotExist:
        # Handle the case where the user does not have an FCM token
        return None

    result = push_service.notify_single_device(
        registration_id=token,
        message_title=title,
        message_body=message,
        data_message=data
    )
    return result


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = None
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group if previously joined
        if self.room_name is not None:
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'join_room':
            room_name = text_data_json['roomName']
            caller = text_data_json['caller'] if 'caller' in text_data_json else None
            calling_id = text_data_json['callingID'] if 'callingID' in text_data_json else None
            join_call_or_not = text_data_json['join'] if 'join' in text_data_json else None

            await self.join_room(room_name, caller, calling_id, join_call_or_not)

        elif message_type == 'offer':
            offer = text_data_json['offer']
            print("offer",offer)
            print('------------------------------------------------------------------------------------------------------')
            await self.send_group_message(self.room_name, 'offer_message', {'offer': offer})

        elif message_type == 'answer':
            answer = text_data_json['answer']
            print("answer",answer)
            print('------------------------------------------------------------------------------------------------------')
            await self.send_group_message(self.room_name, 'answer_message', {'answer': answer})

        elif message_type == 'ice':
            ice = text_data_json['ice']
            print(ice)
            await self.send_group_message(self.room_name, 'ice_message', {'ice': ice})

    async def join_room(self, room_name, caller, calling_id, join_call_or_not):
        if (calling_id != None):
            user = User.objects.get(pk=calling_id)
            profile = Profile.objects.get(user=user)

            send_push_notification(
                user,
                "Calling",
                f"{user.username} is calling you!",
                {
                    "caller": user.username,
                    "user_picture": profile.profile_picture.url,
                    "roomName": room_name
                }
            )

        self.room_name = room_name.replace("/", "_")
        await self.channel_layer.group_add(room_name.replace("/", "_"), self.channel_name)
        await self.channel_layer.group_send(room_name.replace("/", "_"), {
            'type': 'welcome_message',
            'caller': caller,
            'message': 'joined_call' if join_call_or_not else 'rejected_call'
        })

    async def send_group_message(self, room, message_type, message):
        if room:
            await self.channel_layer.group_send(room, {
                'type': message_type,
                **message
            })

    # Custom handlers for group messages
    async def welcome_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'welcome_message',
            'caller': event['caller'],
            'message': event['message'],
        }))

    async def offer_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'offer',
            'offer': event['offer']
        }))

    async def answer_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'answer': event['answer']
        }))

    async def ice_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'ice',
            'ice': event['ice']
        }))
