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
            print("original_achievement:", original_achievement)
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