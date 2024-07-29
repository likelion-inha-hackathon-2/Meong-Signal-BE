# chat/serializers.py

from rest_framework import serializers
from .models import ChatRoom, Message

class MessageSerializer(serializers.ModelSerializer):

    sender_profile_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'sender_profile_image', 'content', 'timestamp', 'read']

    def get_sender_profile_image(self, obj):
        return obj.sender.profile_image.url if obj.sender.profile_image else None

class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = ['id', 'owner_user', 'user_user']

class ChatRoomInfoSerializer(serializers.ModelSerializer):
    other_user_nickname = serializers.CharField()
    other_user_profile_image = serializers.ImageField()
    last_message_content = serializers.CharField()
    last_message_timestamp = serializers.DateTimeField()
    other_user_id = serializers.IntegerField()
    other_user_representative = serializers.BooleanField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'other_user_nickname', 'other_user_id','other_user_profile_image', 'other_user_representative', 'last_message_content', 'last_message_timestamp']