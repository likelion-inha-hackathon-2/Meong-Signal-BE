from django.shortcuts import render
from django.shortcuts import get_object_or_404

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
from .utils import get_distance


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
    serializer = DogRegisterSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        serializer.save()
        return Response({"message" : "강아지가 등록되었습니다."},status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=400)

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
    method="GET", 
    tags=["강아지 api"],
    operation_summary="심심한 강아지 목록 조회 api"
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def boring_dog_list(request):
    dogs = Dog.objects.filter(status = 'B') # 심심한 강아지 목록
    user_address = request.user.road_address # 사용자의 위치(도로명주소)
    return_data = {"dogs" : []}

    # 사용자와의 거리가 2km 이내인 강아지 필터링
    for dog in dogs:
        dog_user_id = dog.user_id.id
        dog_user =  User.objects.get(id=dog_user_id) # 견주
        dog_user_address = dog_user.road_address # 견주의 위치(도로명주소)
        distance = get_distance(user_address, dog_user_address)

        if distance != -1 and distance < 2000: # 경로를 찾은 경우 and 경로가 2km 이내인 경우
            boring_dog = {"id":dog.id, "name":dog.name, "road_address":dog_user.road_address, "distance":round(distance / 1000, 1), "image":dog.image.url}
            return_data["dogs"].append(boring_dog)

    return Response(return_data, status=status.HTTP_200_OK)