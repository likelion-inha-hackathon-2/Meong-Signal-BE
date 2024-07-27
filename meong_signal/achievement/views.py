from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Sum, Avg

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
from .models import *
from review.models import *

import pandas as pd
from datetime import datetime, timedelta
from geopy.distance import geodesic

# Create your views here.

@swagger_auto_schema(
    method="POST",
    tags=["achievement api"],
    operation_summary="업적 생성 api(client는 사용하지 않는 api입니다.)",
    request_body=AchievementSerializer
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def new_achievement(request):
    if request.data['category'] not in ('dog', 'walking'):
        return Response({"error" : "category는 dog, walking만 입력 가능합니다."}, status=400)
    serializer = AchievementSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=200)
    return Response(serializer.errors, status=400)

@swagger_auto_schema(
    method="GET",
    tags=["achievement api"],
    operation_summary="업적 조회 api",
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def get_achievement(request):
    user_id = request.user.id
    return_data = {"dog":[], "walking":[]}

    achievements = UserAchievement.objects.filter(user_id = user_id)
    for achievement in achievements:
        achievement_data = {}
        try:
            original_achievement = Achievement.objects.get(id = achievement.achievement_id.id)
        except ObjectDoesNotExist:
            return Response({"error" : "User에 관한 Achievement를 찾을 수 없습니다."}, status=400)

        category = original_achievement.category
        achievement_data["title"] = original_achievement.title
        achievement_data["total_count"] = float(original_achievement.total_count)
        achievement_data["now_count"] = float(achievement.count)
        achievement_data["is_representative"] = float(achievement.is_representative)
        achievement_data["is_achieved"] = float(achievement.is_achieved)
        achievement_data["id"] = achievement.id

        return_data[category].append(achievement_data)

    return Response(return_data, status=200)

@swagger_auto_schema(
    method="POST",
    tags=["achievement api"],
    operation_summary="현재 회원에 대한 업적 생성 api(client는 사용하지 않는 api입니다. 업적 목록이 보이지 않을 시 실행해주세요.)"
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def new_achievement_about_user(request):
    user = request.user
    achievements = Achievement.objects.all()
    for achievement in achievements:
        if not UserAchievement.objects.filter(achievement_id = achievement, user_id = user).exists():
            UserAchievement.objects.create(achievement_id = achievement, user_id = user, count = 0)
    return Response({"message": "회원과 관련된 업적이 생성되었습니다."}, status=200)

@swagger_auto_schema(
    method="POST",
    tags=["achievement api"],
    operation_summary="대표 업적으로 설정하는 api",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='user_achievement_id'),
        }
    ),
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def set_representative(request):

    user_achievement_id = request.data['id']
    try:
        achievement = UserAchievement.objects.get(id = user_achievement_id)
    except ObjectDoesNotExist:
        return Response({"error" : "id에 대한 UserAchievement를 찾을 수 없습니다."}, status=400)

    # 기존 대표로 등록되어있던 업적이 있으면 대표에서 해제
    try:
        rep_achievement = UserAchievement.objects.get(user_id = request.user.id, is_representative = True)
        rep_achievement.is_representative = False
        rep_achievement.save()
    except ObjectDoesNotExist:
        pass
    
    if achievement.is_representative:
        return Response({"message": "이미 대표로 등록된 업적입니다."}, status=200)

    if achievement.is_achieved:
        achievement.is_representative = True
        achievement.save()
        return Response({"message": "대표로 등록되었습니다."}, status=200)

    return Response({"message": "아직 완료되지 않은 업적입니다."}, status=400)

@swagger_auto_schema(
    method="GET",
    tags=["achievement api"],
    operation_summary="대표 업적 조회 api",
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def get_represent(request):
    user_id = request.user.id
    return_data = {"title" : "", "id" : 0}
    try:
        rep_achievement = UserAchievement.objects.get(user_id = user_id, is_representative = True)
        try:
            original_achievement = Achievement.objects.get(id = rep_achievement.achievement_id.id)
            title = original_achievement.title
            return_data["title"] = title
        except:
            return Response({"error":"업적 정보 찾기 실패"}, status=400)
        return_data["id"] = rep_achievement.id
    except ObjectDoesNotExist:
        pass
    return Response(return_data, status=200)