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
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='R')
    image = models.ImageField(upload_to='dogs', default='dogs/default_dog.png')
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.image:
            self.image = 'dogs/default_dog.png'
        super().save(*args, **kwargs)

class DogTag(models.Model):
    dog_id = models.ForeignKey(Dog, on_delete=models.CASCADE)
    number = models.IntegerField()
    count = models.IntegerField(default=1)

    def __str__(self):
        r = f'DOG {self.dog_id.name}의 {self.number}번 칭호'
        return r