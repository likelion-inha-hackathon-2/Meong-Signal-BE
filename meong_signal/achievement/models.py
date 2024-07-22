from django.db import models
from account.models import User

# Create your models here.
class Achievement(models.Model):
    title = models.CharField(max_length=20)
    total_count = models.DecimalField(max_digits=5, decimal_places=1)
    category = models.CharField(max_length=20)
    def __str__(self):
        return self.title

class UserAchievement(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement_id = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    count = models.DecimalField(max_digits=5, decimal_places=1)
    is_representative = models.BooleanField(default=False)
    is_achieved = models.BooleanField(default=False)

    def __str__(self):
        r = f'USER {self.user_id.nickname}의 업적 \'{self.achievement_id.title}\''
        return r

