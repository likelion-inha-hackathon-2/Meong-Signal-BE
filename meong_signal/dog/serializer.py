from rest_framework import serializers
from .models import *
#from account.models import User
#from account.serializer import *

class DogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dog
        fields = ('name', 'gender', 'age', 'introduction')

    def create(self, validated_data):
        return Dog.objects.create(**validated_data)

class DogTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = DogTag
        fields = ('number',)

class DogRegisterSerializer(serializers.Serializer):
    dog = DogSerializer()
    tags = DogTagSerializer(many=True)

    def create(self, validated_data):
        dog_data = validated_data['dog']
        user = self.context['request'].user  # JWT 인증을 통해 로그인된 사용자 정보 가져오기

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