from rest_framework import serializers
from .models import *

class UserReviewRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReview
        fields = '__all__'