import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializer import *

from account.models import User
from dog.models import Dog

#############################
# 새로운 약속을 생성하는 api

@swagger_auto_schema(
    method="post",
    tags=["약속 api"],
    operation_summary="새로운 약속 생성",
    request_body=ScheduleSerializer,
    responses={
        201: ScheduleSerializer,
        400: "Bad Request",
    }
)
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
# 얼마 남지 않은 약속 목록을 반환하는 api + 지난 약속 종료 처리

@swagger_auto_schema(
    method="get",
    tags=["약속 api"],
    operation_summary="남은 시간이 3일 이하인 약속 목록 조회",
    responses={
        200: ScheduleSerializer(many=True),
        400: "Bad Request",
    }
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def get_upcoming_schedules(request):
    user = request.user
    now = datetime.datetime.now()
    three_days_later = now + timedelta(days=3)
    one_day_ago = now - timedelta(days=1)

    #3일 이하로 남은 약속들
    upcoming_schedules = Schedule.objects.filter(
        Q(user_id=user.id) | Q(owner_id=user.id),
        time__range=(now, three_days_later),
        status='W'
    )

    #약속 시간에서 하루 지난 약속들은 종료 처리
    past_schedules = Schedule.objects.filter(user_id = user.id, time__lte=one_day_ago, status='W')
    past_schedules.update(status='F')

    serializer = ScheduleSerializer(upcoming_schedules, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#############################

#############################
#약속 수정 api

# 수정 가능한 정보 : [시간, 약속이름, 상태]
# 수정 불가한 정보 : [id, 견주 id, 강아지 id, 유저 id]

@swagger_auto_schema(
    method="PUT",
    tags=["약속 api"],
    operation_summary="약속 정보 수정 api",
    request_body=ScheduleUpdateSerializer,
    responses={
        200: ScheduleUpdateSerializer,
        400: 'Bad Request',
        401: 'Unauthorized'
    }
)
@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
def update_schedule(request, schedule_id):
    user = request.user
    data = request.data
    try:
        schedule = Schedule.objects.get(id = schedule_id)
        
    except:
        return Response({"error" : "id에 맞는 약속 정보를 확인할 수 없습니다."}, status=400)

    if 'status' in data:
        if data["status"] not in ('W', 'R', 'F'):
            return Response({"error" : "status는 W, R, F중에서만 설정 가능합니다."}, status=400)
        
    serializer = ScheduleUpdateSerializer(schedule, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message':'정상적으로 수정되었습니다.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#############################
# Walking중인 내 강아지와 산책자 정보 구하는 api

@swagger_auto_schema(
    method="get",
    tags=["약속 api"],
    operation_summary="Walking중인 내 강아지와 산책자 정보 구하는 api",
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def get_walking_dogs(request):
    walking_dogs_info = {"walking_dogs" : []}
    user = request.user

    schedules = Schedule.objects.filter(owner_id = user, status = 'R')
    for schedule in schedules:
        dog_id = schedule.dog_id.id
        dog_image = schedule.dog_id.image.url
        dog_name = schedule.dog_id.name
        walk_user_id = schedule.user_id.id

        walking_dog_info = {"dog_id" : dog_id, "dog_image" : dog_image, "dog_name" : dog_name, "walk_user_id" : walk_user_id}
        walking_dogs_info["walking_dogs"].append(walking_dog_info)
        
    return Response(walking_dogs_info, status=200)

#############################
# 약속 삭제 api

@swagger_auto_schema(
    method="delete",
    tags=["약속 api"],
    operation_summary="약속 삭제",
    responses={
        204: "No Content",
        404: "Not Found",
    }
)
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
def delete_appointment(request, app_id):
    try:
        appointment = Schedule.objects.get(id=app_id)
        appointment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Schedule.DoesNotExist:
        return Response({'error': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)
    
############################
