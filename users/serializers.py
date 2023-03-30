from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('bio', 'profile_picture')

class FriendsSerialzer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Profile

class ProfileSerialzer(serializers.ModelSerializer):
    chat_friend = FriendsSerialzer(many=True)
    class Meta:
        fields = "__all__"
        model = Profile

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email address is already in use.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already in use.")
        return value

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user