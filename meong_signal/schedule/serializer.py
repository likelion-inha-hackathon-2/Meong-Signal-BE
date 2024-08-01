from rest_framework import serializers
from .models import Schedule

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id','user_id', 'owner_id', 'dog_id', 'name', 'time', 'status']

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