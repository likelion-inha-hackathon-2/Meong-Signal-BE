from rest_framework import serializers
from datetime import date
from account.models import *
from .models import *
from .utils import *

class RoadAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('road_address',)

class TrailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trail
        fields = '__all__'

class WalkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Walk
        fields = '__all__'

class WalkInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Walk
        fields = ('dog_id', 'time', 'meong', 'distance',)

class WalkRegisterSerializer(serializers.Serializer):
    walk = WalkInfoSerializer()

    def create(self, validated_data):
        user = self.context['request'].user
        walk_data = validated_data['walk']
        kilocalories = get_calories(walk_data['time'], float(walk_data['distance']))
        walk = Walk.objects.create(user_id=user, kilocalories=kilocalories, date=date.today(), **walk_data)

        return walk

