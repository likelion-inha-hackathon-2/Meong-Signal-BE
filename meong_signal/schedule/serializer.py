from rest_framework import serializers
from .models import Schedule
from chat.models import ChatRoom

class ScheduleSerializer(serializers.ModelSerializer):
    room_id = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ['id','room_id','user_id', 'owner_id', 'dog_id', 'name', 'time', 'status']

    def get_room_id(self, obj):
        chatroom = ChatRoom.objects.filter(owner_user=obj.owner_id, user_user=obj.user_id).first()
        return chatroom.id if chatroom else None


class ScheduleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ('id', 'time', 'name', 'status')
    
    def update(self, instance, validated_data):

        include_fields = ['time', 'name', 'status']

        for field in include_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save()
        return instance