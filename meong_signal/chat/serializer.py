# chat/serializers.py

from rest_framework import serializers
from .models import ChatRoom, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'read']

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['id', 'owner_user', 'user_user']

class ChatRoomInfoSerializer(serializers.ModelSerializer):
    other_user_nickname = serializers.CharField()
    other_user_profile_image = serializers.ImageField()
    last_message_content = serializers.CharField()
    last_message_timestamp = serializers.DateTimeField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'other_user_nickname', 'other_user_profile_image', 'last_message_content', 'last_message_timestamp']