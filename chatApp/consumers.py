import asyncio
import json
from uuid import uuid4
import tempfile
from django.core.files import File
from .models import ChatVideo
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
from chatApp.Utilities.imageKeys import imageKeys
from .models import ChatImage


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
        self.temp_file = None
        self.chunks = []
        self.chat_message_video = None

    async def connect(self):
        token = self.scope['query_string'].decode('utf-8')
        token = token[6:]
        user = await get_user_from_token(token)
        username = user.username
        
        self.user_one = self.scope['url_route']['kwargs']['user_one']
        self.user_two = self.scope['url_route']['kwargs']['user_two']

        self.room_name = self.user_one + self.user_two
        self.room_group_name = "chat_%s" % self.room_name
        if(username == self.user_one or username == self.user_two):
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
            if text_data_json["type"] == "message":
                # Create a temporary file to store the incoming video chunks
                radon_title = str(uuid4())
                message = text_data_json["message"]
                user = text_data_json["user"]

                sender = await sync_to_async(get_object_or_404)(Profile, username=user["username"])
                # Make a chat message model
                chat_message = await sync_to_async(ChatMessage.objects.create)(
                    sender=sender,
                    content=message
                )

                # Add images
                if(text_data_json["image_length"] != 0):
                    image_keys = (imageKeys(
                        text_data_json, ChatImage, radon_title, user["username"]
                    ))
                    chatroom_context = await sync_to_async(lambda: chat_message.images)()
                    if image_keys:
                        for i in image_keys:
                            await sync_to_async(chatroom_context.add)(i)

                #Add it to the chatroom
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
            if text_data_json["type"] == "incoming":
                user = text_data_json["user"]
                sender = await sync_to_async(get_object_or_404)(Profile, username=user["username"])
                self.chat_message_video = await sync_to_async(ChatMessage.objects.create)(
                    sender=sender,
                    content=""
                )

            if text_data_json["type"] == "title":
                if self.temp_file:  # Close the previous temporary file, if any
                    self.temp_file.close()
                self.temp_file = tempfile.NamedTemporaryFile(delete=False)
                self.chunks = []

            if text_data_json["type"] == "end":
                # Join the chunks to create the final video buffer
                video_buffer = b''.join(self.chunks)

                # Write the video buffer to the temporary file
                self.temp_file.write(video_buffer)
                self.temp_file.flush()  # Ensure that all data has been written to the file
                self.temp_file.seek(0)  # Reset the file pointer to the beginning of the file

                video = await sync_to_async(ChatVideo.objects.create)(
                    name="sender"
                )
                with open(self.temp_file.name, 'rb') as f:
                    video.video.save("sender.mp4", File(f))
                video.save()
                print("Closed")
                
                # Add video to chatmessage
                chat_message_id = self.chat_message_video.id
                chat_message = await sync_to_async(get_object_or_404)(ChatMessage, id=chat_message_id)
                chat_video_context = await sync_to_async(lambda: chat_message.videos)()
                await sync_to_async(chat_video_context.add)(video)

                #Add it to the chatroom
                chat_room = await sync_to_async(get_object_or_404)(
                    ChatRoom, name=f"{self.user_one}/{self.user_two}"
                )
                chat_context = await sync_to_async(lambda: chat_room.chatContext)()
                await sync_to_async(chat_context.add)(chat_message)

            if text_data_json["type"] == "allvideocame":
                # Send video message to room group
                chat_message_id = self.chat_message_video.id
                chat_message = await sync_to_async(get_object_or_404)(ChatMessage, id=chat_message_id)
                serilizer = await sync_to_async(ChatMessageSerialzer)(chat_message)
                
                await self.channel_layer.group_send(
                    self.room_group_name, {
                        "type": "chat_message", 
                        "chat": serilizer.data
                    }
                )

        elif bytes_data:
            # Start a new task to handle video data
            asyncio.create_task(self.process_video_data(bytes_data))

    # Write the received chunk to the temporary file
    async def process_video_data(self, bytes_data):
        print("Writing...")
        self.chunks.append(bytes_data)

    # Receive message from room group
    async def chat_message(self, event):
        chat = event["chat"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "chat": chat
        }))