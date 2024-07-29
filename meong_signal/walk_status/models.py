from django.db import models

class Owner(models.Model): # 위치 받는 사람
    owner_id = models.IntegerField(unique=True)

class WalkUser(models.Model): # 위치 보내는 사람
    walk_user_id = models.IntegerField(unique=True)

class WalkRoom(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    walk_user = models.ForeignKey(WalkUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('owner', 'walk_user')
        
class Location(models.Model):
    room = models.ForeignKey(WalkRoom, on_delete=models.CASCADE, related_name="locations")
    walk_user_id = models.IntegerField() # 위치를 보내는, 산책하는 WalkUser의 이메일
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)  # 위도
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)  # 경도
