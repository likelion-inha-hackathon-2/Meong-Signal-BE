# serializers.py

# rest_framework의 serializers 모듈을 임포트합니다.
from rest_framework import serializers
# 현재 디렉토리의 models 모듈에서 WalkRoom, Location 모델을 임포트합니다.
from .models import WalkRoom, Location

# Message 모델에 대한 시리얼라이저 클래스입니다.
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location  # Message 모델을 기반으로 합니다.
        fields = "__all__"  # 모든 필드를 포함시킵니다.

# WalkRoom 모델에 대한 시리얼라이저 클래스입니다.
class WalkRoomSerializer(serializers.ModelSerializer):
    #latest_latitude = serializers.SerializerMethodField()  # 최신 latitude 필드를 동적으로 가져옵니다.
    #latest_longitude = serializers.SerializerMethodField()  # 최신 longitude 필드를 동적으로 가져옵니다.
    owner_id = serializers.SerializerMethodField()  # 견주 이메일 필드를 동적으로 가져옵니다.
    walk_user_id = serializers.SerializerMethodField()  # 산책자 이메일을 가져오는 필드입니다.
    locations = LocationSerializer(many=True, read_only=True, source="locations.all")  # 해당 위치 정보 목록을 가져옵니다.

    class Meta:
        model = WalkRoom  # WalkRoom 모델을 기반으로 합니다.
        # 시리얼라이즈할 필드들을 지정합니다.
        fields = ('id', 'owner_id', 'walk_user_id', 'locations')

    # shop_user의 이메일을 반환하는 메소드입니다.
    def get_owner_id(self, obj):  
        return obj.owner.owner_id

    # visitor_user의 이메일을 반환하는 메소드입니다.
    def get_walk_user_id(self, obj):  
        return obj.walk_user.walk_user_id