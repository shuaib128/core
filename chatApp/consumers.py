import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatMessage, ChatRoom
from asgiref.sync import sync_to_async
from users.models import Profile
from django.shortcuts import get_object_or_404
from .serializers import ChatMessageSerialzer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth import get_user_model


"""
Given a JWT token, return the user object.
"""


async def get_user_from_token(token):
    # Convert the synchronous get_user_model function to an asynchronous function
    get_user_model_async = sync_to_async(get_user_model, thread_sensitive=True)

    try:
        # Get the validated token object from the raw token
        validated_token = await sync_to_async(JWTAuthentication().get_validated_token, thread_sensitive=True)(raw_token=token)

        # Get the user object from the validated token object
        user_id = validated_token[api_settings.USER_ID_CLAIM]
        user_model = await get_user_model_async()
        user = await sync_to_async(user_model.objects.get, thread_sensitive=True)(pk=user_id)

        return user

    except InvalidToken:
        # Invalid token
        return None


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect(self):
        token = self.scope['query_string'].decode('utf-8')
        token = token[6:]
        user = await get_user_from_token(token)
        username = user.username

        self.user_one = self.scope['url_route']['kwargs']['user_one']
        self.user_two = self.scope['url_route']['kwargs']['user_two']

        self.room_name = self.user_one + self.user_two
        self.room_group_name = "chat_%s" % self.room_name
        
        if (username == self.user_one or username == self.user_two):
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            print(text_data_json)
            if text_data_json["type"] == "message":
                message = text_data_json["message"]
                user = text_data_json["user"]

                sender = await sync_to_async(get_object_or_404)(Profile, username=user["username"])
                # Make a chat message model
                chat_message = await sync_to_async(ChatMessage.objects.create)(
                    sender=sender,
                    content=message
                )

                # Add it to the chatroom
                chat_room = await sync_to_async(get_object_or_404)(
                    ChatRoom, name=f"{self.user_one}/{self.user_two}"
                )
                chat_context = await sync_to_async(lambda: chat_room.chatContext)()
                await sync_to_async(chat_context.add)(chat_message)

                # Send message to room group
                serilizer = await sync_to_async(ChatMessageSerialzer)(chat_message)
                await self.channel_layer.group_send(
                    self.room_group_name, {
                        "type": "chat_message",
                        "chat": serilizer.data
                    }
                )

    # Receive message from room group
    async def chat_message(self, event):
        chat = event["chat"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "chat": chat
        }))

    # Receive message from room group
    async def update_chat(self, event):
        chat_id = event["chat_id"]
        Chat = await self.get_chat(chat_id)
        serilizer = await sync_to_async(ChatMessageSerialzer)(Chat)

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "chat": serilizer.data
        }))

    @sync_to_async
    def get_chat(self, chat_id):
        return ChatMessage.objects.get(id=chat_id)