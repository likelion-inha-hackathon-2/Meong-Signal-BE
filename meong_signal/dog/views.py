from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from pathlib import Path
from .serializer import *
from walk.serializer import WalkSerializer, DogWalkRegisterSerializer
from walk.models import Walk
from .utils import finding_dogs_around_you
from django.http import QueryDict


##########################################
# api 1 : 강아지 등록
@swagger_auto_schema(
    method="POST", 
    tags=["강아지 api"],
    operation_summary="강아지 추가 api", 
    request_body=DogRegisterSerializer
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def new_dog(request):
    data = request.data
    if isinstance(request.data, QueryDict):
        data = QueryDict.dict(data)
        
    dog_serializer = DogSerializer(data=data, context={'request': request})

    # 데이터에서 tags에 해당하는 키를 찾아 리스트에 추가
    tags_data = []
    if len(tags_data) > 3:
        return Response("error:태그의 최초 등록은 3개까지 가능합니다.", status=400)

    for key, value in data.items():
        if key.startswith('tags['):  # 키가 'tags['로 시작하는지 확인
            value = int(value)
            # tags의 숫자 부분을 파싱하여 리스트에 추가
            index = int(key.split('[')[1].split(']')[0])  # 'tags[0]'에서 숫자만 추출
            tags_data.append({
                'number': value
            })
            if value < 1 or value > 9:
                return Response("error:태그 번호는 1번부터 9번까지만 가능합니다.", status=400)

    if dog_serializer.is_valid():
        dog = dog_serializer.save()  # Dog 인스턴스 생성 및 저장

        for tag_data in tags_data:
            DogTag.objects.create(dog_id = dog, number = tag_data['number'])

        return Response({"message" : "강아지가 등록되었습니다."}, status=200)

    return Response(dog_serializer.errors, status=400)

##########################################

##########################################
# api 2 : 강아지 상태 변경

@swagger_auto_schema(
    method="PATCH", 
    tags=["강아지 api"],
    operation_summary="강아지 상태 변경 api", 
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'status': openapi.Schema(type=openapi.TYPE_STRING, description='new status'),
        }
    ),
)
@api_view(['PATCH'])
@authentication_classes([JWTAuthentication])
def update_dog_status(request, dog_id):
    dog = get_object_or_404(Dog, pk=dog_id)
    new_status = request.data.get('status', None)

    if new_status not in ['R', 'B', 'W']:
        return Response({'error': 'status는 R, B, W중에서만 입력 가능합니다.'}, status=status.HTTP_400_BAD_REQUEST)

    if new_status is not None:
        dog.status = new_status
        dog.save()
        return Response({"message" : "강아지가 정보가 수정되었습니다."},status=status.HTTP_200_OK)
    
    return Response({'error': '유효하지 않은 요청입니다.'}, status=status.HTTP_400_BAD_REQUEST)

##########################################

##########################################
# api 3 : 보유 강아지 목록 조회 api

@swagger_auto_schema(
    method="GET", 
    tags=["강아지 api"],
    operation_summary="강아지 목록 조회 api"
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def dog_list(request):
    user = request.user
    if user is None:
        return Response({"error" : "유저가 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    dogs = Dog.objects.filter(user_id = user.id)
    if not dogs: # 강아지가 한 마리도 없는 경우
        return Response({"dogs":[]}, status=status.HTTP_200_OK)
    
    serializer = DogInfoSerializer(dogs, many=True)
    return Response({"dogs": serializer.data}, status=status.HTTP_200_OK)

##########################################

##########################################
# api 4 : 심심한 상태의 강아지 조회 api

@swagger_auto_schema(
    method="POST", 
    tags=["강아지 api"],
    operation_summary="심심한 강아지 목록 조회 api",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='현재 위도'),
            'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='현재 경도'),
        }
    ),
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def boring_dog_list(request):
    dogs = Dog.objects.filter(status = 'B') # 심심한 강아지 목록
    try:
        return_data = finding_dogs_around_you(request.data['latitude'], request.data['longitude'],  dogs)
    except:
        return Response({"message":"심심한 강아지를 불러오는데 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    if 'error' in return_data:
        return Response({"message": return_data['error']}, status=status.HTTP_400_BAD_REQUEST)
    return Response(return_data, status=status.HTTP_200_OK)

##########################################

##########################################
# api 5 : 강아지 대표 태그(3개) 조회 api

@swagger_auto_schema(
    method="GET", 
    tags=["강아지 api"],
    operation_summary="강아지 대표 태그 3개 조회 api"
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def get_representative_tags(request, dog_id):
    dog = Dog.objects.get(id = dog_id)
    if not dog:
        return Response({"error" : "dog_id에 대응하는 강아지가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)
    
    tags = DogTag.objects.filter(dog_id = dog.id)
    if not tags: # 강아지에 대한 태그가 없는 경우
        return Response({"tags" : []}, status=status.HTTP_200_OK)
    
    tags = dog.dogtag_set.all().order_by('-count')[:3]  # 태그 조회 및 빈도수 기준 내림차순 정렬
    
    if not tags:
        return Response({"tags": []}, status=status.HTTP_200_OK)
    
    serializer = DogTagSerializer(tags, many=True)
    return Response({"tags": serializer.data}, status=status.HTTP_200_OK)

##########################################

##########################################
# api 6 : 태그별 강아지 조회 -> 반경 2km 이내만 return

@swagger_auto_schema(
    method="POST", 
    tags=["강아지 api"],
    operation_summary="태그별 강아지 조회 api",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='현재 위도'),
            'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='현재 경도'),
        }
    ),
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def search_by_tag(request, tag_number):

    dog_tags = DogTag.objects.filter(number = tag_number)
    dogs = [dog_tag.dog_id for dog_tag in dog_tags] # 특정 태그 강아지 목록

    try:
        return_data = finding_dogs_around_you(request.data['latitude'], request.data['longitude'],  dogs)
    except:
        return Response({"message":"강아지를 불러오는데 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    if 'error' in return_data:
        return Response({"message": return_data['error']}, status=status.HTTP_400_BAD_REQUEST)

    return Response(return_data, status=status.HTTP_200_OK)

##########################################

##########################################
# api 7 : 특정 강아지 정보 조회 api
@swagger_auto_schema(
    method="GET", 
    tags=["강아지 api"],
    operation_summary="특정 강아지 조회 api"
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def dog_info(request, dog_id):
    dog = Dog.objects.get(id = dog_id)
    if dog is None:
        return Response({"error":"dog_id에 대한 강아지가 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
    dog_serializer = DogInfoWithStatusSerializer(dog)

    walks = Walk.objects.filter(dog_id = dog_id)
    walk_serializer = DogWalkRegisterSerializer(walks, many=True)

    return Response({"dog":dog_serializer.data, "walks":walk_serializer.data}, status=status.HTTP_200_OK)

##########################################


##########################################
# api 8 : 모든 상태의 강아지 조회 api

@swagger_auto_schema(
    method="POST", 
    tags=["강아지 api"],
    operation_summary="모든 강아지 목록 조회 api",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='현재 위도'),
            'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='현재 경도'),
        }
    ),
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def all_status_dog_list(request):
    dogs = Dog.objects.all() # 모든
    try:
        return_data = finding_dogs_around_you(request.data['latitude'], request.data['longitude'],  dogs)
    except:
        return Response({"message":"강아지를 불러오는데 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    if 'error' in return_data:
        return Response({"message": return_data['error']}, status=status.HTTP_400_BAD_REQUEST)
    return Response(return_data, status=status.HTTP_200_OK)

##########################################

##########################################
# api 9 : 특정 강아지 주인의 이메일 조회 api
@swagger_auto_schema(
    method="POST", 
    tags=["강아지 api"],
    operation_summary="견주 이메일 조회 api",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'dog_id': openapi.Schema(type=openapi.TYPE_NUMBER, description='강아지 Id'),
        }
    ),
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def get_owner_email(request):
    dog_id = request.data["dog_id"]
    try:
        dog = Dog.objects.get(id = dog_id)
        owner = User.objects.get(id = dog.user_id.id)
        return Response({"owner_email" : owner.email}, status=status.HTTP_200_OK)

    except:
        return Response({"error":"dog_id에 대한 강아지가 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

##########################################


dummy_data = {
  "dogs": [
    {
      "id": 1,
      "name": "관리자2의강아지",
      "road_address": "미추홀구 인하로 100",
      "distance": 0.5,
      "image": "https://meong-signal-s3-bucket.s3.ap-northeast-2.amazonaws.com/dogs/cdf354c07a6647fa85c262bd5ddd6bba.JPG",
      "status": "B"
    },
    {
      "id": 2,
      "name": "절미",
      "road_address": "미추홀구 인하로 100",
      "distance": 0.5,
      "image": "https://meong-signal-s3-bucket.s3.ap-northeast-2.amazonaws.com/dogs/711f0d3fee264d658b48518779f29e2c.png",
      "status": "R"
    },
    {
      "id": 6,
      "name": "밥풀이",
      "road_address": "인천 미추홀구 경인남길 118",
      "distance": 0.3,
      "image": "https://meong-signal-s3-bucket.s3.ap-northeast-2.amazonaws.com/dogs/182b947ca82a48039b0bad4354c260e9.jpg",
      "status": "R"
    }
  ],
  "count": 3
}

# dummy api : 모든 상태의 강아지 조회 api

@swagger_auto_schema(
    method="POST", 
    tags=["강아지 api"],
    operation_summary="모든 상태 강아지 조회 dummy api",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'latitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='현재 위도'),
            'longitude': openapi.Schema(type=openapi.TYPE_NUMBER, description='현재 경도'),
        }
    ),
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def dummy_all_status(request):
    return Response(dummy_data, status=200)

