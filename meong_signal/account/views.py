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


# 구글 프로필사진 형식: JPEG 또는 PNG만
# 카카오 이미지 경우 640 x 640px 사이즈를 권장하며 최대 10MB의 jpg, jpeg, png 파일만 지원합니다
# 네이버 프로필 사진은 20MB 이하의 JPG, JPEG, GIF, PNG 파일을 등록할 수 있습니다.
# jpg, jpeg, png, gif
def get_file_extension_from_mime_type(content_type):
    mime_to_extension = {
        'image/jpeg': 'jpg',
        'image/png': 'png'
    }
    
    return mime_to_extension.get(content_type, '')

def remove_profile_image(query_dict):
    # QueryDict를 일반 dict로 변환
    data_dict = query_dict.dict()
    
    # 'profile_image' 키를 삭제
    if 'profile_image' in data_dict:
        del data_dict['profile_image']
    
    # dict를 다시 QueryDict로 변환
    updated_query_dict = QueryDict('', mutable=True)
    updated_query_dict.update(data_dict)
    
    return updated_query_dict

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
    print("request.data:", data)
    print("social_id:", data["social_id"])
    if "social_id" not in data or data["social_id"] == "No": # 일반 로그인인 경우
        print("일반로그인입니다.")
        if data["profile_image"] == "null": # 프로필사진을 등록하지 않은 경우
            data = remove_profile_image(data)
        serializer = UserSerializer(data = data)
    else: # 소셜 로그인인 경우, 이미지를 url로 받아오기 때문에 따로 처리
        print("소셜로그인입니다.")
        dict_data = QueryDict.dict(data)

        response = requests.get(dict_data["profile_image"])
        image_file = BytesIO(response.content)
        content_type = response.headers['Content-Type']

        file_extension = dict_data["profile_image"].split('.')[-1]
        if file_extension not in ('jpeg', 'jpg', 'gif', 'png'):
            file_extension = get_file_extension_from_mime_type(content_type)

        new_file_name = generate_uuid_filename(file_extension)

        temp_file = TemporaryUploadedFile(
            name=new_file_name,
            content_type=content_type, 
            size=len(response.content),
            charset=None
        )

        temp_file.write(response.content)
        temp_file.seek(0)
        
        filtered_data = {key: value for key, value in data.items() if key != "profile_image"}
        filtered_data["profile_image"] = temp_file

        print("filtered_data:", filtered_data)
        serializer = UserSerializer(data = filtered_data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': '201', 'message': 'All data added successfully'}, status=201)
        else:
            print("serializer.errors:", serializer.errors)  # 유효성 검사 에러 출력
            return Response({'status': '400', 'message': serializer.errors}, status=400)

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
        user_social_id = str(user_information["id"])
        user = User.objects.get(social_id = user_social_id)
        token = RefreshToken.for_user(user)
        return Response({'is_user' : 1, 'refresh_token': str(token),
                        'access_token': str(token.access_token), }, status=status.HTTP_200_OK)

    except User.DoesNotExist: # 회원가입 필요한 경우, 일단 프론트로 유저 정보 넘기고, 도로명주소 포함해서 다시 signup 요청하게 함!
        return Response({"is_user" : 0, "social_id":user_social_id, "email" : user_information['kakao_account']['email'], "nickname":user_information['properties']['nickname'], "profile_image" : user_information["properties"]["profile_image"]}, status=200)


##########################################
# 소셜 로그인: 네이버

@api_view(['POST'])
@permission_classes([AllowAny])
def naver_login_callback(request):
    # 인가 코드를 받아서 토큰 받아와서 로그인 or 회원가입 요청하기
    data = {
        "grant_type" : "authorization_code",
        "client_id" : get_secret("NAVER_CLIENT_ID"),
        "client_secret" : get_secret("NAVER_CLIENT_SECRET"),
        "code" : request.data["code"],
        "state" : request.data["state"]
    }

    naver_token_url = "https://nid.naver.com/oauth2.0/token" # 토큰 받아오는 api
    access_token = requests.post(naver_token_url, data=data).json()['access_token']

    naver_user_api = "https://openapi.naver.com/v1/nid/me" # 유저 정보 받아오는 api
    header = {"Authorization" : f"Bearer {access_token}"}
    
    user_information_result = requests.get(naver_user_api, headers=header).json()
    if user_information_result["message"] == "success": # 정보 조회 성공한 경우
        user_information = user_information_result["response"]
        try: # 회원가입 되어있는 유저인 경우, 토큰 return
            user = User.objects.get(social_id = user_information["id"])
            token = RefreshToken.for_user(user)
            return Response({'is_user' : 1, 'refresh_token': str(token),
                            'access_token': str(token.access_token), }, status=status.HTTP_200_OK)

        except User.DoesNotExist: # 회원가입 필요한 경우, 일단 프론트로 유저 정보 넘기고, 도로명주소 포함해서 다시 signup 요청하게 함!
            return Response({"is_user" : 0, "social_id":user_information["id"], "email" : user_information['email'], "nickname":user_information['nickname'], "profile_image" : user_information["profile_image"]}, status=200)
    return Response({"error" : "회원 찾기 실패"},status=400)


##########################################
# 소셜 로그인: 구글

@api_view(['POST'])
@permission_classes([AllowAny])
def google_login_callback(request):
    # 인가 코드를 받아서 토큰 받아와서 로그인 or 회원가입 요청하기
    data = {
        "grant_type" : "authorization_code",
        "client_id" : get_secret("GOOGLE_CLIENT_ID"),
        "client_secret" : get_secret("GOOGLE_CLIENT_SECRET"),
        "redirect_uri" : get_secret("GOOGLE_REDIRECT_URL"),
        "code" : request.data["code"]
    }

    kakao_token_url = "https://oauth2.googleapis.com/token" # 토큰 받아오는 api
    access_token = requests.post(kakao_token_url, data=data).json()['access_token']
    

    kakao_user_api = "https://www.googleapis.com/userinfo/v2/me" # 유저 정보 받아오는 api
    header = {"Authorization" : f"Bearer {access_token}"}
    
    user_information = requests.get(kakao_user_api, headers=header).json()

    try: # 회원가입 되어있는 유저인 경우, 토큰 return
        user_social_id = str(user_information["id"])
        user = User.objects.get(social_id = user_social_id)
        token = RefreshToken.for_user(user)
        return Response({'is_user' : 1, 'refresh_token': str(token),
                        'access_token': str(token.access_token), }, status=status.HTTP_200_OK)

    except User.DoesNotExist: # 회원가입 필요한 경우, 일단 프론트로 유저 정보 넘기고, 도로명주소 포함해서 다시 signup 요청하게 함!
        return Response({"is_user" : 0, "social_id":user_social_id, "email" : user_information['email'], "nickname":user_information['name'], "profile_image" : user_information["picture"]}, status=200)
    
@swagger_auto_schema(
    method="GET",
    tags=["account api"],
    operation_summary="사용자 이메일 확인",
    responses={
        200: UserInfoSerializer,
        401: 'Unauthorized'
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def get_user_email(request):
    user = request.user
    if user is None:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({"my_email":user.email}, status=status.HTTP_200_OK)
