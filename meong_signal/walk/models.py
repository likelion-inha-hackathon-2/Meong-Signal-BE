from django.db import models
from account.models import User
from dog.models import Dog

class Walk(models.Model):
    user_id = models.ForeignKey(User, related_name="user_walks_walker", on_delete=models.CASCADE) # 산책한 유저의 id
    owner_id = models.ForeignKey(User, related_name="user_walks_owner", on_delete=models.CASCADE) # 강아지를 빌려준 견주의 id
    dog_id = models.ForeignKey(Dog, on_delete=models.CASCADE)
    distance = models.DecimalField(max_digits=10, decimal_places=1)
    kilocalories = models.DecimalField(max_digits=10, decimal_places=1)
    time = models.IntegerField()
    date = models.DateField()
    image = models.ImageField(upload_to='walks', default='walks/default_walk.png')
    
    def save(self, *args, **kwargs):
        if not self.image:
            self.image = 'walks/default_walk.png'
        super().save(*args, **kwargs)

class Trail(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=10)
    distance = models.CharField(max_length=10) 
    total_time = models.CharField(max_length=10)

    def __str__(self):
        return self.name
