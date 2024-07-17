from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            nickname=validated_data['nickname'],
            road_address=validated_data.get('road_address', ''),
            detail_address=validated_data.get('detail_address', ''),
            meong=validated_data.get('meong', 0),
            total_distance=validated_data.get('total_distance', 0),
            total_kilocalories=validated_data.get('total_kilocalories', 0),
            profile_image=validated_data.get('profile_image', '')
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