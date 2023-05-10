from rest_framework import serializers
from users.models import Profile
from .models import ChatRoom, ChatMessage, ChatImage, ChatVideo

class ImagesSerialzer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ChatImage

class VideosSerialzer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = ChatVideo

class ProfileSerialzer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Profile

class ChatMessageSerialzer(serializers.ModelSerializer):
    sender = ProfileSerialzer()
    images = ImagesSerialzer(many=True)
    videos = VideosSerialzer(many=True)
    class Meta:
        fields = "__all__"
        model = ChatMessage

class CharroomSerialzer(serializers.ModelSerializer):
    chatContext = ChatMessageSerialzer(many=True)
    members = ProfileSerialzer(many=True)
    class Meta:
        fields = "__all__"
        model = ChatRoom