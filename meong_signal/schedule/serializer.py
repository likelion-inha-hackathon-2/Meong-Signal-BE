from rest_framework import serializers
from .models import Schedule

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id','user_id', 'owner_id', 'dog_id', 'name', 'time', 'status']
