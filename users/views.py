from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer, ProfileUpdateSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth import get_user_model
import base64
from django.shortcuts import get_object_or_404
from .models import Profile
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .serializers import ProfileSerialzer
from django.core.files.base import ContentFile

class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


# Decode the token payload to get the user ID
def get_user_from_token(token):
    try:
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        User = get_user_model()
        user = User.objects.get(pk=user_id)
        return user
    except:
        return None
class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve the JWT token from the request header
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return Response({'error': 'Authorization header is missing'})

        auth_header_parts = auth_header.split(' ')
        if len(auth_header_parts) != 2 or auth_header_parts[0] != 'Bearer':
            return Response({'error': 'Authorization header is not in the correct format'})

        token = auth_header_parts[1]

        # Retrieve the authenticated user from the token
        user = get_user_from_token(token)
        profile = get_object_or_404(Profile, user=str(user.id))
        serilizer = ProfileSerialzer(profile)

        # Return a response
        return Response(serilizer.data)
    

class ProfileUpdateAPIView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    
    def update(self, request, *args, **kwargs):
        profile = self.get_object()

        # Save the profile picture from the base64-encoded data
        image_data = request.data.get('profile_picture', None)
        if image_data is not None:
            format, imgstr = image_data.split(';base64,') # assuming that imageData is in format "data:image/png;base64,iVBORw0KG..."
            ext = format.split('/')[-1]
            profile.profile_picture.save(f'{profile.id}_profile_picture.{ext}', ContentFile(base64.b64decode(imgstr)), save=False)
            profile.save()

        # Call the parent update() method to save the other fields
        return super().update(request, *args, **kwargs)
    

class LogoutView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data['refreshToken']
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response(
                {'detail': 'Failed to logout. Please try again.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            {'detail': 'You have successfully logged out.'}, 
            status=status.HTTP_200_OK
        )

class SearchUserView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        if request.data != "":
            filtered_users = Profile.objects.filter(username__contains=request.data)
            serialized_data = ProfileSerialzer(filtered_users, many=True).data
            return Response(serialized_data)

        else:
            return Response("No user found")
        
class AddToFriendList(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_object = request.user
        selected_user = request.data["selectedUser"]

        user = get_object_or_404(Profile, username=user_object.username)
        
        user.chat_friend.add(selected_user["id"])
        user.save()
        serialized_data = ProfileSerialzer(user).data

        return Response(serialized_data)