from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.core.files.uploadedfile import TemporaryUploadedFile

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
import requests
import json
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from django.http import QueryDict
from io import BytesIO

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
    data = request.data
    if "social_id" in data: # 소셜 로그인인 경우, 이미지를 url로 받아오기 때문에 따로 처리
        dict_data = QueryDict.dict(data)

        response = requests.get(dict_data["profile_image"])
        image_file = BytesIO(response.content)
        file_extension = dict_data["profile_image"].split('.')[-1]
        new_file_name = generate_uuid_filename(file_extension)

        temp_file = TemporaryUploadedFile(
            name=new_file_name,
            content_type='image/jpeg',  
            size=len(response.content),
            charset=None
        )

        temp_file.write(image_file.getvalue())
        filtered_data = {key: value for key, value in data.items() if key != "profile_image"}
        filtered_data["profile_image"] = temp_file

        serializer = UserSerializer(data = filtered_data)

    else:
        serializer = UserSerializer(data = data)

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

BASE_DIR = Path(__file__).resolve().parent.parent

secret_file = BASE_DIR / 'secrets.json'

with open(secret_file) as file:
    secrets = json.loads(file.read())

def get_secret(setting,secrets_dict = secrets):
    try:
        return secrets_dict[setting]
    except KeyError:
        error_msg = f'Set the {setting} environment variable'
        raise ImproperlyConfigured(error_msg)

##########################################
# 소셜 로그인: 카카오

@api_view(['POST'])
@permission_classes([AllowAny])
def kakao_login_callback(request):
    # 인가 코드를 받아서 토큰 받아와서 로그인 or 회원가입 요청하기
    data = {
        "grant_type" : "authorization_code",
        "client_id" : get_secret("KAKAO_CLIENT_ID"),
        "redirect_uri" : get_secret("KAKAO_REDIRECT_URL"),
        "code" : request.data["code"]
    }

    kakao_token_url = "https://kauth.kakao.com/oauth/token" # 토큰 받아오는 api
    access_token = requests.post(kakao_token_url, data=data).json()['access_token']

    kakao_user_api = "https://kapi.kakao.com/v2/user/me" # 유저 정보 받아오는 api
    header = {"Authorization" : f"Bearer {access_token}"}
    
    user_information = requests.get(kakao_user_api, headers=header).json()

    try: # 회원가입 되어있는 유저인 경우, 토큰 return
        user = User.objects.get(social_id = user_information["id"])
        token = RefreshToken.for_user(user)
        return Response({'is_user' : 1, 'refresh_token': str(token),
                        'access_token': str(token.access_token), }, status=status.HTTP_200_OK)

    except User.DoesNotExist: # 회원가입 필요한 경우, 일단 프론트로 유저 정보 넘기고, 도로명주소 포함해서 다시 signup 요청하게 함!
        return Response({"is_user" : 0, "social_id":user_information['id'], "email" : user_information['kakao_account']['email'], "nickname":user_information['properties']['nickname'], "profile_image" : user_information["properties"]["profile_image"]}, status=200)
