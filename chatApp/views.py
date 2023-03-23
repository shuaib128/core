from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import Profile
from .models import ChatRoom
from .serializers import CharroomSerialzer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

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