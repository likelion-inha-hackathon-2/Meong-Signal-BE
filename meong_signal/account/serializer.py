
from rest_framework import serializers
from .models import *
from achievement.models import *
import uuid
from django.core.files.base import ContentFile
import requests

def generate_uuid_filename(extension):
    unique_id = uuid.uuid4().hex
    return f'{unique_id}.{extension}'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):

        if 'profile_image' in validated_data and ('social_id' not in validated_data or validated_data["social_id"] == "no"): # 일반 회원가입 중 프로필사진 입력한 경우
            # 파일의 확장자 추출
            image = validated_data['profile_image']
            print("image:", image)

            file_extension = image.name.split('.')[-1]
            
            # UUID를 사용한 새 파일 이름 생성
            new_file_name = generate_uuid_filename(file_extension)

            # 파일을 메모리에 저장
            temp_file = ContentFile(image.read())
            temp_file.name = new_file_name

            validated_data['profile_image'] = temp_file

        user = User.objects.create(**validated_data)

        # 회원가입과 동시에 회원의 업적 생성
        achievements = Achievement.objects.all()
        for achievement in achievements:
            UserAchievement.objects.create(achievement_id = achievement, user_id = user, count = 0)

        user.set_password(validated_data['password'])
        user.save()
        return user

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'nickname', 'road_address', 'detail_address', 'profile_image', "total_distance", "total_kilocalories")

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('nickname', 'road_address', 'detail_address', 'profile_image')
    
    def update(self, instance, validated_data):

        include_fields = ['nickname', 'road_address', 'detail_address', 'profile_image']

        for field in include_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save()
        return instance

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'
        