from django.db import models
from account.models import User
from dog.models import Dog

class ChatRoom(models.Model):
    owner_user = models.ForeignKey(User, related_name='owner_user_chatroom', on_delete=models.CASCADE)
    user_user = models.ForeignKey(User, related_name='user_user_chatroom', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    dog_id=models.ForeignKey(Dog, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('owner_user', 'user_user')

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f'{self.owner_user.nickname} - {self.user_user.nickname}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'견주 {self.owner_user.nickname}님과 이용자 {self.user_user.nickname}님의 채팅방'
    
class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    owner_read = models.BooleanField(default=False)
    user_read = models.BooleanField(default=False)

    def __str__(self):
        return self.content