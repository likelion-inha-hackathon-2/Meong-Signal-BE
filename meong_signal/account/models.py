from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class UserManager(BaseUserManager):
    def create_user(self, email, pwd, **extra_fields):
        if not email:
            raise ValueError('The email field must be set')
        user = self.model(email=email, **extra_fields)
        user.set_password(pwd)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, pwd, **extra_fields):

        #필요에 따라 주석처리
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        ######

        return self.create_user(email, pwd, **extra_fields)

class User(AbstractBaseUser):
    email = models.EmailField(max_length=50, unique=True)
    pwd = models.CharField(max_length=200)
    nickname = models.CharField(max_length=10)
    #도로명주소
    address_name = models.CharField(max_length=10, blank=True)
    #상세 주소
    road_address = models.CharField(max_length=200, null=True, blank=True)
    meong = models.IntegerField(default=0)
    total_distance = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    total_kilocalories = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    profile_image = models.CharField(max_length=150, null=True, default='https://blog.kakaocdn.net/dn/GHYFr/btrsSwcSDQV/UQZxkayGyAXrPACyf0MaV1/img.jpg')
