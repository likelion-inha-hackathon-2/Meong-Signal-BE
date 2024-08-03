from rest_framework import serializers
from datetime import date
from account.models import *
from .models import *
from .utils import *
import uuid
from django.core.files.base import ContentFile
from review.models import UserReview
from django.core.exceptions import ObjectDoesNotExist

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

def generate_uuid_filename(extension):
    unique_id = uuid.uuid4().hex
    return f'{unique_id}.{extension}'

class WalkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Walk
        fields = '__all__'

class WalkInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Walk
        fields = ['dog_id', 'time', 'distance', 'image']

class WalkRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Walk
        fields = ['dog_id', 'time', 'distance']

    def create(self, validated_data):

        user = self.context['request'].user # 산책한 사람

        dog = Dog.objects.select_related('user_id').get(id = validated_data['dog_id'].id) # 관련된 user 객체도 가져옴
        owner = dog.user_id

        kilocalories = get_calories(validated_data['time'], float(validated_data['distance']))
        walk = Walk.objects.create(user_id=user, owner_id = owner, image = dog.image, kilocalories=kilocalories, date=date.today(), **validated_data)
        return walk

# 강아지 정보 조회할 때 필요한 산책에 대한 정보
class DogWalkRegisterSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField() # 같이 산책한 사람의 nickname
    is_reviewed = serializers.SerializerMethodField()

    class Meta:
        model = Walk
        fields = ['id', 'distance', 'nickname', 'date', 'is_reviewed']
    
    def get_nickname(self, obj):
        return obj.user_id.nickname if obj.user_id else None

    def get_is_reviewed(self, obj): # 견주 입장에서 작성한 리뷰()가 있는지
        try:
            UserReview.objects.get(owner_id = obj.owner_id.id, walk_id = obj.id)
            # 리뷰 작성한경우
            return 1
        except ObjectDoesNotExist:
            return 0
        