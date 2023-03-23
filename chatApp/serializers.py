from rest_framework import serializers
from users.models import Profile
from .models import ChatRoom, ChatMessage

class ProfileSerialzer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Profile

class ChatMessageSerialzer(serializers.ModelSerializer):
    sender = ProfileSerialzer()
    class Meta:
        fields = "__all__"
        model = ChatMessage

class CharroomSerialzer(serializers.ModelSerializer):
    chatContext = ChatMessageSerialzer(many=True)
    members = ProfileSerialzer(many=True)
    class Meta:
        fields = "__all__"
        model = ChatRoom