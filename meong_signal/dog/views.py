from django.shortcuts import render

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
