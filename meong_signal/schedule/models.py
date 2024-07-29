from django.db import models
from account.models import User
from dog.models import Dog

class Schedule(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_shcedules_walker")
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_shcedules_owner")
    dog_id = models.ForeignKey(Dog, on_delete=models.CASCADE)

    name = models.CharField(max_length=20)
    time = models.DateTimeField() # YYYY-MM-DD HH:MM:SS 형식

    STATUS_CHOICES = [
        ('W', 'Waiting'),
        ('R', 'Running'),
        ('F', 'Finish')
    ]
    
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='W')

    def __str__(self):
        return self.name
