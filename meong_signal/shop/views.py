
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



##########################################
# 상품 등록 api

@swagger_auto_schema(
    method="POST", 
    tags=["멍샵 api"],
    operation_summary="상품 등록 api", 
    request_body=ProductRegisterSerializer
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def product(request):
    serializer = ProductRegisterSerializer(data = request.data)

    if serializer.is_valid():
        serializer.save()
        return Response({'status':'201','message': 'product data added successfully'}, status=201)
    return Response({'status':'400','message':serializer.errors}, status=400)
##########################################

##########################################
# 카테고리별 상품 return api

@swagger_auto_schema(
    method="GET", 
    tags=["멍샵 api"],
    operation_summary="카테고리별 상품 조회 api", 
    response={200: ProductReturnSerializer(many=True)}
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def category_product(request, category):
    try:
        if not category:
            return Response({"error": "Category parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        products = PRODUCTS.objects.filter(category=category)
        
        if not products.exists():
            return Response({"error": "No products found for the given category."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductReturnSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

##########################################

##########################################
# 상품 구매 (멍 차감 & 보유 상품 목록에 추가) api

@swagger_auto_schema(
    method="POST", 
    tags=["멍샵 api"],
    operation_summary="상품 구매 api",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='상품 ID')
        }
    )
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def purchase_product(request):
    try:
        product_id = request.data.get('product_id')
        user = request.user
        
        if not product_id:
            return Response({"error": "Product ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        print("product_id:", product_id, "user_id:", user.id)
        
        try: # 이미 구매한 상품인 경우 error
            _ = UserProducts.objects.get(product_id = product_id, user_id = user.id)
            return Response({"error": "이미 구매하신 상품입니다."}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            pass
        
        product = PRODUCTS.objects.get(id=product_id)
        user = User.objects.get(id=user.id)
        
        if user.meong < product.price:
            return Response({"error": "Not enough meong to purchase the product."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.meong -= product.price
        user.save()

        UserProducts.objects.create(product_id = product, user_id = user) # 유저가 구매한 상품 목록에 추가
        
        return Response({"message": "Product purchased successfully.", "current_meong":user.meong}, status=status.HTTP_200_OK)
    
    except PRODUCTS.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
##########################################

##########################################
# 입력한만큼 meong을 충전

@swagger_auto_schema(
    method="POST", 
    tags=["멍샵 api"],
    operation_summary="충전 api", 
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'meong': openapi.Schema(type=openapi.TYPE_INTEGER, description='충전할 멍')
        }
    )
)
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def charger_meong(request):
    try:
        meong_to_charge = request.data.get('meong')
        user = request.user
        user.meong += int(meong_to_charge)
        user.save()

        return Response({"message": "Meong charged successfully.", "current_meong": user.meong}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

##########################################

##########################################
# 현재 멍 return

@swagger_auto_schema(
    method="GET", 
    tags=["멍샵 api"],
    operation_summary="현재 멍 조회 api"
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def return_meong(request):
    user = request.user

    return Response({"current_meong": user.meong}, status=status.HTTP_200_OK)

##########################################

##########################################
# 구매한 상품 get

@swagger_auto_schema(
    method="GET", 
    tags=["멍샵 api"],
    operation_summary="구매한 상품 조회 api"
)
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
def my_products(request):
    user = request.user
    return_data = {"my_products" : []}

    my_products = UserProducts.objects.filter(user_id = user.id)
    for my_product in my_products:
        product_info = {}
        try:
            product = PRODUCTS.objects.get(id = my_product.product_id.id)
            product_info["name"] = product.name
            product_info["image"] = product.image.url
            product_info["content"] = product.content
            product_info["price"] = product.price

            return_data["my_products"].append(product_info)
        except ObjectDoesNotExist:
            return Response({"error" : "상품 정보가 존재하지 않습니다."}, status=400)


    return Response(return_data, status=status.HTTP_200_OK)