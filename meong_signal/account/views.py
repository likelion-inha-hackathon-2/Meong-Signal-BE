from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User
from .serializer import *


##########################################
# api 1 : 회원가입

@swagger_auto_schema(
        method="POST", 
        tags=["회원 api"],
        operation_summary="회원가입", 
        request_body=UserSerializer
)
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data = request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({'status':'201','message': 'All data added successfully'}, status=201)
    return Response({'status':'400','message':serializer.errors}, status=400)

##########################################

##########################################
# api 2 : 로그인 

@swagger_auto_schema(
        method="POST", 
        tags=["account api"],
        operation_summary="로그인", 
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User login Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
            }
        ),
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):

    email = request.data.get('email')
    password = request.data.get('password')

    user = authenticate(email=email, password=password)


    if user is None:
        return Response({'status':'401', 'message': '이메일 또는 비밀번호가 일치하지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    token = RefreshToken.for_user(user)
    update_last_login(None, user)

    return Response({'status':'200', 'refresh_token': str(token),
                    'access_token': str(token.access_token), }, status=status.HTTP_200_OK)

##########################################

##########################################
# api 3 : 사용자 정보 확인

@swagger_auto_schema(
    method="GET",
    tags=["account api"],
    operation_summary="사용자 정보 확인",
    responses={
        200: UserInfoSerializer,
        401: 'Unauthorized'
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def get_user_info(request):
    user = request.user
    print("user_id:", user.id)
    if user is None:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserInfoSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

##########################################

##########################################
# api 4 : 사용자 정보 수정

# 수정 가능한 정보 : [주소, 닉네임, 프로필 사진]
# 수정 불가한 정보 : [이메일, 패스워드, 멍, is_staff, is_superuser, 총 이동거리, 총 소비 칼로리]

@swagger_auto_schema(
    method="PUT",
    tags=["account api"],
    operation_summary="사용자 정보 수정",
    request_body=UserUpdateSerializer,
    responses={
        200: UserUpdateSerializer,
        400: 'Bad Request',
        401: 'Unauthorized'
    }
)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
def update_user_info(request):
    user = request.user
    serializer = UserUpdateSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message':'정상적으로 수정되었습니다.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

##########################################