from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.db import IntegrityError

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from account.models import User
from .serializer import *
from .utils import *
from .models import *

import pandas as pd
from geopy.distance import geodesic

#csv 데이터 로드
def load_trail_data():
    trail_data = pd.read_csv('static/dox/KC_CFR_WLK_STRET_INFO_2021.csv')
    return trail_data


######################################
# 집 주소를 위도, 경도로 변환하여 user 모델에 저장하는 api

@swagger_auto_schema(
    method="POST",
    tags=["walk api"],
    operation_summary="위도, 경도 변환",
    request_body = RoadAddressSerializer
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def coordinate(request):
    user = request.user
    serializer = RoadAddressSerializer(data = request.data)

    if serializer.is_valid():
        road_address = serializer.validated_data['road_address']
        result = coordinate_send_request(road_address)
        latitude = result["documents"][0]['y']
        longitude = result["documents"][0]['x']
        
        user.latitude = latitude
        user.longitude = longitude
        user.save()

        return Response({"road_address": road_address, "latitude": latitude, "longitude": longitude}, status=201)
    return Response({'status': '400', 'message': serializer.errors}, status=400)

######################################


######################################
# 가까운 산책로 데이터 DB에 저장하는 api

@swagger_auto_schema(
    method="POST",
    tags=["walk api"],
    operation_summary="가까운 산책로 데이터 저장",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='집 주소의 위도'),
            'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='집 주소의 경도')
        }
    ),
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def save_nearby_trails(request):
    user = request.user
    latitude = user.latitude
    longitude = user.longitude

    if not latitude or not longitude:
        return Response({'status': '400', 'message': 'Latitude and longitude are required.'}, status=400)

    trail_data = load_trail_data()

    # 거리 계산
    trail_data['distance'] = trail_data.apply(
        lambda row: geodesic((latitude, longitude), (row['COURS_SPOT_LA'], row['COURS_SPOT_LO'])).kilometers, axis=1
    )

    nearest_trails = trail_data.nsmallest(2, 'distance')

    for _, row in nearest_trails.iterrows():
        try:
            Trail.objects.create(
                user_id=user,
                name=row['WLK_COURS_FLAG_NM'],
                level=row['COURS_LEVEL_NM'],
                distance=row['COURS_LT_CN'],
                total_time=row['COURS_TIME_CN'],
                selected=False
            )
        except IntegrityError:
            continue

    return Response({'status': '201', 'message': 'Nearby trails saved successfully.'}, status=201)