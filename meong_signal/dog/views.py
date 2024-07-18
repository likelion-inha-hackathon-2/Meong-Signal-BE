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