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

# 작성한 리뷰 전체 조회

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
    print("user_reviews:", user_reviews)

    # 내가 남긴 산책에 대한 리뷰 -> WalkingReview중 user_id가 내 id
    walk_reviews = WalkingReview.objects.filter(user_id = user.id)
    print("walk_reviews:", walk_reviews)


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
# api 1 : 리뷰 작성(견주 입장, 별점달린 리뷰)

@swagger_auto_schema(
    method="POST", 
    tags=["리뷰 api"],
    operation_summary="견주 입장 리뷰 작성 api(별점달린 리뷰입니다.)", 
    request_body=UserReviewSerializer
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def new_review_rating(request):
    data=request.data
    data['owner_id'] = request.user.id
    walk = Walk.objects.get(id=data['walk_id'])
    user = walk.user_id
    data['user_id'] = user.id
    serializer = UserReviewSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
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
    serializer = WalkReviewRegisterSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({"message" : "리뷰가 등록되었습니다."},status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=400)

##########################################



######## 테스트용 dummy api ###########

dummy_review = {
	"user_review" : [
		{
			"evaluated_user_name" : "사용자1",
			"evaluated_user_profile" : "media/users/IMG_123.jpg",
			"rating" : 2,
			"content" : "강아지가 산책을 다녀오고 조금 힘들어해요."
		},
		{
			"evaluated_user_name" : "사용자2",
			"evaluated_user_profile" : "media/users/IMG_123.jpg",
			"rating" : 5,
			"content" : "저희 제제를 예뻐해주셔서 감사해요!"
		}
	],
	"walking_review" : [
		{
			"evaluated_user_name" : "제제주인",
			"evaluated_user_profile" : "media/dogs/jeje.jpg",
			"content" : "견주님이 착하시고 강아지가 체력이 좋아요.",
			"tag" : [
				{
					"number" : "2"
				},
				{
					"number" : "3"
				}
			]
		},
		{
			"evaluated_user_name" : "사용자3",
			"evaluated_user_profile" : "media/dogs/julmiii.jpg",
			"content" : "시간 약속을 잘 지켜주셔서 좋았어요",
			"tag" : [
				{
					"number" : "1"
				},
				{
					"number" : "6"
				}
			]
		}
	]
}

@swagger_auto_schema(
    method="GET", 
    tags=["리뷰 api"],
    operation_summary="(dummy) 받은 리뷰 조회 api"
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def get_received_reviews(request):

    return Response(dummy_review, status=status.HTTP_200_OK)

#####################################

######## 테스트용 dummy api ###########