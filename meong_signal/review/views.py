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
import json

from .serializer import *
from walk.models import Walk


##########################################
# api 1 : 리뷰 작성(견주 입장, 별점달린 리뷰)

@swagger_auto_schema(
    method="POST", 
    tags=["리뷰 api"],
    operation_summary="견주 입장 리뷰 작성 api(별점달린 리뷰입니다.)", 
    request_body=UserReviewInputSerializer
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def new_review_rating(request):
    data=request.data
    data['owner_id'] = request.user.id

    try:
        walk = Walk.objects.get(id=data['walk_id'])
    except ObjectDoesNotExist:
        return Response({"error" : "walk id에 대한 산책 기록을 찾을 수 없습니다."}, status=400)

    if request.user != walk.owner_id: # 리뷰를 작성하려는 사람이 해당 산책의 견주가 아닌 경우 error
        return Response({"error" : "내 강아지의 산책 기록이 아닙니다."}, status=400)
    
    try: # 이미 리뷰를 작성한 경우 error
        UserReview.objects.get(walk_id = data["walk_id"], owner_id = request.user.id)
        return Response({"error" : "이미 해당 산책에 대한 리뷰를 작성했습니다."}, status=409)
    except:
        pass

    if data['meong'] > request.user.meong: # 보유 멍보다 선물할 멍 값이 큰 경우
        return Response({"error" : "보유한 멍보다 선물할 멍의 값이 큽니다."}, status=400)

    user = walk.user_id
    data['user_id'] = user.id
    serializer = UserReviewSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        # 멍 차감
        request.user.meong -= data["meong"]
        request.user.save()
        # 멍 지급
        user.meong += data["meong"]
        user.save()
        return Response({"message" : "리뷰가 등록되었습니다.", "data" : serializer.data},status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=400)

##########################################

##########################################
# api 2 : 리뷰 작성(사용자 입장, 태그달린 리뷰)

@swagger_auto_schema(
    method="POST", 
    tags=["리뷰 api"],
    operation_summary="사용자 입장 리뷰 작성 api(태그달린 리뷰입니다.)", 
    request_body=WalkReviewRegisterSerializer
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def new_review_tags(request):
    data = request.data
    try:
        walk = Walk.objects.get(id=data['review']['walk_id'])
    except ObjectDoesNotExist:
        return Response({"error" : "walk id에 대한 산책 기록을 찾을 수 없습니다."}, status=400)
    
    if request.user != walk.user_id: # 리뷰를 작성하려는 사람이 해당 산책의 산책자가 아닌 경우 error
        return Response({"error" : "내 산책 기록이 아닙니다."}, status=400)
        
    try: # 이미 리뷰를 작성한 경우 error
        WalkingReview.objects.get(walk_id = data['review']["walk_id"], user_id = request.user.id)
        return Response({"error" : "이미 해당 산책에 대한 리뷰를 작성했습니다."}, status=409)
    except:
        pass

    if data['meong'] > request.user.meong: # 보유 멍보다 선물할 멍 값이 큰 경우
        return Response({"error" : "보유한 멍보다 선물할 멍의 값이 큽니다."}, status=400)
    
    owner = walk.owner_id
    print("owner:", owner)
    serializer = WalkReviewRegisterSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        # 멍 차감
        request.user.meong -= data["meong"]
        request.user.save()
        # 멍 지급
        owner.meong += data["meong"]
        owner.save()
        return Response({"message" : "리뷰가 등록되었습니다."},status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=400)

##########################################

##########################################
# api 3 : 작성한 리뷰 조회 api

@swagger_auto_schema(
    method="GET", 
    tags=["리뷰 api"],
    operation_summary="작성한 리뷰 조회 api"
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def get_written_reviews(request):
    return_data = {"user_review" : [], "walking_review" : []}
    user = request.user

    # 내가 남긴 유저에 대한 리뷰 -> UserReview중 owner_id가 내 id
    user_reviews = UserReview.objects.filter(owner_id = user.id)

    # 내가 남긴 산책에 대한 리뷰 -> WalkingReview중 user_id가 내 id
    walk_reviews = WalkingReview.objects.filter(user_id = user.id)

    for user_review in user_reviews:
        evaluated_user = user_review.user_id
        return_data["user_review"].append({"evaluated_user_name":evaluated_user.nickname, "evaluated_user_profile":evaluated_user.profile_image.url, "rating":user_review.rating, "content":user_review.content})
    
    for walk_review in walk_reviews:
        evaluated_user = walk_review.owner_id
        tags = ReviewTag.objects.filter(review_id = walk_review.id)
        tags_list = [{"number": tag.number} for tag in tags]
        return_data["walking_review"].append({"evaluated_user_name":evaluated_user.nickname, "evaluated_user_profile":evaluated_user.profile_image.url, "content":walk_review.content, "tags" : tags_list})

    return Response(return_data, status=status.HTTP_200_OK)

##########################################

##########################################
# api 4 : 받은 리뷰 조회 api

@swagger_auto_schema(
    method="GET", 
    tags=["리뷰 api"],
    operation_summary="받은 리뷰 조회 api"
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def get_received_reviews(request):
    return_data = {"user_review" : [], "walking_review" : []}
    user = request.user

    # 내가 받은 "유저에 대한 리뷰" -> UserReview중 user_id가 내 id
    user_reviews = UserReview.objects.filter(user_id = user.id)

    # 내가 받은 "산책에 대한 리뷰" -> WalkingReview중 owner_id가 내 id
    walk_reviews = WalkingReview.objects.filter(owner_id = user.id)

    for user_review in user_reviews:
        evaluated_user = user_review.user_id
        return_data["user_review"].append({"evaluated_user_name":evaluated_user.nickname, "evaluated_user_profile":evaluated_user.profile_image.url, "rating":user_review.rating, "content":user_review.content})
    
    for walk_review in walk_reviews:
        evaluated_user = walk_review.owner_id
        tags = ReviewTag.objects.filter(review_id = walk_review.id)
        tags_list = [{"number": tag.number} for tag in tags]
        return_data["walking_review"].append({"evaluated_user_name":evaluated_user.nickname, "evaluated_user_profile":evaluated_user.profile_image.url, "content":walk_review.content, "tags" : tags_list})

    return Response(return_data, status=status.HTTP_200_OK)
