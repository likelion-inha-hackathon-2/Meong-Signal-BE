from rest_framework import serializers
from account.models import *
from .models import *

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'