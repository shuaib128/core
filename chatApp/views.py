import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import Profile
from .models import ChatRoom, ChatMessage, MediaFile
from .serializers import CharroomSerialzer, ChatMessageSerialzer, MediaSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your views here.


class CreateRetriveChatroom(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Get page number from URL,
            page_number = request.GET.get('page', 1)
            page_size = 4
            start = (int(page_number) - 1) * page_size
            end = start + page_size

            chatRoom = request.data["chatRoom"]
            user1 = request.data["user"]
            user2 = request.data["selectedUser"]

            members = Profile.objects.filter(username__in=[user1, user2])
            chatroom, created = ChatRoom.objects.get_or_create(
                name=chatRoom
            )
            for member in members:
                chatroom.members.add(member)

            messages = chatroom.chatContext.all()[start:end]

            serilizer = CharroomSerialzer(chatroom)
            return Response(serilizer.data)
        except Exception as e:
            pass
            return Response("404")

# Search Convertation


class ChatMessageSearchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get("message", " ").strip()
        chatRoom = request.data.get("chatroom")

        if not message:
            return Response({'error': 'Search message cannot be empty'})

        chatrooms = ChatRoom.objects.filter(name=chatRoom)
        messages = ChatMessage.objects.filter(
            content__contains=message, ChatContent__in=chatrooms)
        serialized_messages = [ChatMessageSerialzer(m).data for m in messages]
        return Response(serialized_messages)


# Add Image to a chat
class ChatImageCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, format=None):
        try:
            # Once message is saved, broadcast it
            channel_layer = get_channel_layer()

            # Posted data
            chatroomStr = request.data["chatroom"]
            user1, user2 = chatroomStr.split("/")
            chatroom = f"chat_{user1}{user2}"
            chat_id = request.data['postID']
            chat = get_object_or_404(ChatMessage, id=chat_id)

            format, imgstr = request.data['imageBase64'].split(';base64,')
            ext = format.split('/')[-1]
            file_content = ContentFile(
                base64.b64decode(imgstr), name=f"image.{ext}")

            media_file = MediaFile()
            media_file.file.save("image.jpg", file_content)
            chat.media_files.add(media_file)

            # Broadcast message to the chat group
            async_to_sync(channel_layer.group_send)(
                chatroom, 
                {
                    "type": "update_chat",
                    "chat_id": chat.id
                }
            )

            return Response(
                {
                    'message': "image updated",
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Add video to a chat
class ChatVideoCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        try:
            filename = request.data.get('filename')
            chunk = request.data.get('chunk')

            if not filename or not chunk:
                return Response(
                    {'status': 'Bad request'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            media_files = MediaFile.objects.filter(filename=filename)
            if media_files.exists():
                # If a matching MediaFile exists, choose the first one
                media_file = media_files.first()
            else:
                # If no matching MediaFile exists, create a new one
                media_file = MediaFile.objects.create(filename=filename)

            if chunk:
                media_file.append_chunk(chunk)

            serializer = MediaSerializer(media_file)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Add Video file to the Post


class FinalizeUploadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        try:
            # Once message is saved, broadcast it
            channel_layer = get_channel_layer()

            # Posted data
            chatroomStr = request.data["chatroom"]
            user1, user2 = chatroomStr.split("/")
            chatroom = f"chat_{user1}{user2}"
            chat_id = request.data.get('postID')
            video_id = request.data.get('videoID')

            chat = get_object_or_404(ChatMessage, id=chat_id)
            video_file = get_object_or_404(MediaFile, id=video_id)

            chat.media_files.add(video_file)
            chat.save()

            # Broadcast message to the chat group
            async_to_sync(channel_layer.group_send)(
                chatroom, 
                {
                    "type": "update_chat",
                    "chat_id": chat.id
                }
            )

            return Response(
                {"message": "video added"},
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
