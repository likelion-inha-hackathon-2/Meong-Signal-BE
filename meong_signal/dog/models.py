from django.db import models
from account.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Dog(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(30)])
    introduction = models.CharField(max_length=100)
    STATUS_CHOICES = [
        ('B', 'Boring'),
        ('R', 'Relax'),
        ('W', 'Walking')
    ]
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    image = models.CharField(max_length=100, default='../media/user/dafault_user.jpg') # 일단 User 기본 이미지 사용

    def __str__(self):
        return self.name

class DogTag(models.Model):
    dog_id = models.ForeignKey(Dog, on_delete=models.CASCADE)
    number = models.IntegerField()
    count = models.IntegerField()