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

class TrailRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trail
        fields = ('name', 'level', 'distance', 'total_time')

class TrailReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trail
        fields = ('id', 'name', 'level', 'distance', 'total_time',)

class WalkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Walk
        fields = '__all__'

class WalkInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Walk
        fields = ['dog_id', 'time', 'meong', 'distance',]

class WalkRegisterSerializer(serializers.Serializer):
    walk = WalkInfoSerializer()

    def create(self, validated_data):
        user = self.context['request'].user # 산책한 사람

        walk_data = validated_data['walk']
        dog = Dog.objects.select_related('user_id').get(id = walk_data['dog_id'].id) # 관련된 user 객체도 가져옴
        owner = dog.user_id

        kilocalories = get_calories(walk_data['time'], float(walk_data['distance']))
        walk = Walk.objects.create(user_id=user, owner_id = owner, kilocalories=kilocalories, date=date.today(), **walk_data)

        return walk


# 강아지 정보 조회할 때 필요한 산책에 대한 정보
class DogWalkRegisterSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField() # 같이 산책한 사람의 nickname

    class Meta:
        model = Walk
        fields = ['distance', 'nickname', 'date']
    
    def get_nickname(self, obj):
        return obj.user_id.nickname if obj.user_id else None