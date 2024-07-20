from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):

        #필요에 따라 주석처리
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        ######

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=200)
    nickname = models.CharField(max_length=10)
    road_address = models.CharField(max_length=200, null=True) # 도로명주소
    detail_address = models.CharField(max_length=100, null=True, blank = True)
    meong = models.IntegerField(default=0)
    total_distance = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    total_kilocalories = models.DecimalField(max_digits=10, decimal_places=1, default=0)
    profile_image = models.ImageField(upload_to='users', default='users/default_user.jpg')
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)  # 위도
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True) 

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["password", "nickname"]

    def __str__(self):
        return self.nickname


    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    
    def save(self, *args, **kwargs):
        if not self.profile_image:
            self.profile_image = 'users/default_user.jpg'
        super().save(*args, **kwargs)