from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializer import *

from account.models import User
from dog.models import Dog

#############################
# 새로운 약속을 생성하는 api

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def create_schedule(request):
    serializer = ScheduleSerializer(data=request.data)
    if serializer.is_valid():
        owner_id = serializer.validated_data['owner_id']
        dog_id = serializer.validated_data['dog_id']
        
        try:
            dog = Dog.objects.get(id=dog_id.id)
            if dog.user_id.id != owner_id.id:
                return Response({'error': '강아지의 주인이 일치하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        except Dog.DoesNotExist:
            return Response({'error': '일치하는 강아지가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#############################

#############################
# 얼마 남지 않은 약속 목록을 반환하는 api