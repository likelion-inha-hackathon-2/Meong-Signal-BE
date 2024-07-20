from rest_framework import serializers
from .models import *
import uuid
from django.core.files.base import ContentFile

def generate_uuid_filename(extension):
    unique_id = uuid.uuid4().hex
    return f'{unique_id}.{extension}'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        if 'profile_image' in validated_data:
            # 파일의 확장자 추출
            image = validated_data['profile_image']
            file_extension = image.name.split('.')[-1]
            
            # UUID를 사용한 새 파일 이름 생성
            new_file_name = generate_uuid_filename(file_extension)

            # 파일을 메모리에 저장
            temp_file = ContentFile(image.read())
            temp_file.name = new_file_name

            
        user = User(
            email=validated_data['email'],
            nickname=validated_data['nickname'],
            road_address=validated_data.get('road_address', ''),
            detail_address=validated_data.get('detail_address', ''),
            meong=validated_data.get('meong', 0),
            total_distance=validated_data.get('total_distance', 0),
            total_kilocalories=validated_data.get('total_kilocalories', 0),
            profile_image = temp_file
        )

        user.set_password(validated_data['password'])
        user.save()
        return user

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('nickname', 'road_address', 'detail_address', 'profile_image', "total_distance", "total_kilocalories")

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