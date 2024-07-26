from rest_framework import serializers
from datetime import date
from account.models import *
from .models import *
from .utils import *
import uuid
from django.core.files.base import ContentFile

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
        fields = ['dog_id', 'time', 'distance', 'image']

    def create(self, validated_data):
        if 'image' in validated_data:
            # 파일의 확장자 추출
            image = validated_data['image']

            file_extension = image.name.split('.')[-1]
            
            # UUID를 사용한 새 파일 이름 생성
            new_file_name = generate_uuid_filename(file_extension)

            # 파일을 메모리에 저장
            temp_file = ContentFile(image.read())
            temp_file.name = new_file_name

            validated_data['image'] = temp_file

        user = self.context['request'].user # 산책한 사람

        dog = Dog.objects.select_related('user_id').get(id = validated_data['dog_id'].id) # 관련된 user 객체도 가져옴
        owner = dog.user_id

        kilocalories = get_calories(validated_data['time'], float(validated_data['distance']))
        walk = Walk.objects.create(user_id=user, owner_id = owner, kilocalories=kilocalories, date=date.today(), **validated_data)

        return walk


# 강아지 정보 조회할 때 필요한 산책에 대한 정보
class DogWalkRegisterSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField() # 같이 산책한 사람의 nickname

    class Meta:
        model = Walk
        fields = ['id', 'distance', 'nickname', 'date']
    
    def get_nickname(self, obj):
        return obj.user_id.nickname if obj.user_id else None