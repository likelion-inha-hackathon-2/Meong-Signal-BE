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
    owner_email = serializers.SerializerMethodField()  # 견주 이메일 필드를 동적으로 가져옵니다.
    walk_user_email = serializers.SerializerMethodField()  # 산책자 이메일을 가져오는 필드입니다.
    locations = LocationSerializer(many=True, read_only=True, source="locations.all")  # 해당 위치 정보 목록을 가져옵니다.

    class Meta:
        model = WalkRoom  # WalkRoom 모델을 기반으로 합니다.
        # 시리얼라이즈할 필드들을 지정합니다.
        fields = ('id', 'owner_email', 'walk_user_email', 'locations')

    # # 최신 위치를 가져오는 메소드입니다.
    # def get_latest_latitude(self, obj):
    #     latest_loc = Location.objects.filter(room=obj).order_by('-timestamp').first()  # 최신 위치를 조회합니다.
    #     if latest_loc:
    #         return latest_loc.latitude  # 최신 위치의 내용을 반환합니다.
    #     return None  # 메시지가 없다면 None을 반환합니다.
    
    #     # 최신 위치를 가져오는 메소드입니다.
    # def get_latest_longitude(self, obj):
    #     latest_loc = Location.objects.filter(room=obj).order_by('-timestamp').first()  # 최신 위치를 조회합니다.
    #     if latest_loc:
    #         return latest_loc.longitude  # 최신 위치의 내용을 반환합니다.
    #     return None  # 메시지가 없다면 None을 반환합니다.

    # # 요청 사용자와 대화하는 상대방의 이메일을 가져오는 메소드입니다.
    # def get_opponent_email(self, obj):
    #     request_user_email = self.context['request'].query_params.get('email', None)
    #     # 요청한 사용자가 상점 사용자일 경우, 방문자의 이메일을 반환합니다.
    #     if request_user_email == obj.shop_user.shop_user_email:
    #         return obj.visitor_user.visitor_user_email
    #     else:  # 그렇지 않다면, 상점 사용자의 이메일을 반환합니다.
    #         return obj.shop_user.shop_user_email

    # shop_user의 이메일을 반환하는 메소드입니다.
    def get_owner_email(self, obj):  
        return obj.owner.owner_email

    # visitor_user의 이메일을 반환하는 메소드입니다.
    def get_walk_user_email(self, obj):  
        return obj.walk_user.walk_user_email