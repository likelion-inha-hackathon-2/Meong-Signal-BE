from django.db import models
from account.models import User
from dog.models import Dog

class Walk(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    dog_id = models.ForeignKey(Dog, on_delete=models.CASCADE)
    distance = models.DecimalField(max_digits=10, decimal_places=1)
    kilocalories = models.DecimalField(max_digits=10, decimal_places=1)
    meong = models.IntegerField()
    time = models.IntegerField()
    date = models.DateField()

class Trail(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=10)
    distance = models.CharField(max_length=10) # api로부터 바로 얻어오는 값이라 Char로 저장 ex) 10~15km
    total_time = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=20, decimal_places=16, default=0)
    longitude = models.DecimalField(max_digits=20, decimal_places=16, default=0)

    def __str__(self):
        return self.name
