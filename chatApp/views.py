from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import Profile
from .models import ChatRoom, ChatMessage
from .serializers import CharroomSerialzer, ChatMessageSerialzer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q

# Create your views here.
class CreateRetriveChatroom(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            chatRoom = request.data["chatRoom"]
            user1 = request.data["user"]
            user2 = request.data["selectedUser"]

            members = Profile.objects.filter(username__in=[user1, user2])
            chatroom, created  = ChatRoom.objects.get_or_create(
                name=chatRoom
            )
            for member in members:
                chatroom.members.add(member)

            serilizer = CharroomSerialzer(chatroom)
            return Response(serilizer.data)
        except Exception as e:
            pass

        return Response("hey")
    
# Search Convertation
class ChatMessageSearchView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get("message", " ").strip()
        chatRoom = request.data.get("chatroom")
        print(chatRoom)

        if not message:
            return Response({'error': 'Search message cannot be empty'})

        chatrooms = ChatRoom.objects.filter(name=chatRoom)
        print(chatrooms)
        messages = ChatMessage.objects.filter(content__contains=message, ChatContent__in=chatrooms)
        serialized_messages = [ChatMessageSerialzer(m).data for m in messages]
        return Response(serialized_messages)

