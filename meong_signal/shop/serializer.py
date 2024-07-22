from rest_framework import serializers
from .models import *
from django.core.files.base import ContentFile

class ProductRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PRODUCTS
        fields = '__all__'


class ProductReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = PRODUCTS
        fields = ['name', 'price', 'content', 'image']