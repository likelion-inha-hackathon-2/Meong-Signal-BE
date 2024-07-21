from rest_framework import serializers
from .models import *
#from account.models import User
#from account.serializer import *
from walk.models import Walk
from walk.serializer import WalkSerializer
import uuid
from django.core.files.base import ContentFile

class DogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dog
        fields = ('name', 'gender', 'age', 'introduction')

class DogTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DogTag
        fields = ('number',)

def generate_uuid_filename(extension):
    unique_id = uuid.uuid4().hex
    return f'{unique_id}.{extension}'

class DogRegisterSerializer(serializers.Serializer):
    dog = DogSerializer()
    tags = DogTagSerializer(many=True)

    def create(self, validated_data):
        user = self.context['request'].user  # JWT 인증을 통해 로그인된 사용자 정보 가져오기
        dog_data = validated_data['dog']
        if 'image' in validated_data:
            # 파일의 확장자 추출
            image = dog_data['image']
            file_extension = image.name.split('.')[-1]
            
            # UUID를 사용한 새 파일 이름 생성
            new_file_name = generate_uuid_filename(file_extension)

            # 파일을 메모리에 저장
            temp_file = ContentFile(image.read())
            temp_file.name = new_file_name

            dog_data['image'] = temp_file

        dog = Dog.objects.create(user_id=user, **dog_data) # dog 객체 생성

        if 'tags' in validated_data:
            tags_data = validated_data['tags']

            for tag_data in tags_data:
                DogTag.objects.create(dog_id=dog, **tag_data)
            
        return dog

class DogInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dog
        fields = '__all__'

class DogInfoWithStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dog
        fields = ('name', 'gender', 'age', 'introduction', 'status')

class DogWalkInfoSerializer(serializers.Serializer):
    dog = DogSerializer()
    walk = WalkSerializer(many=True)
