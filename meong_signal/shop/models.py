from django.db import models
from account.models import User

class PRODUCTS(models.Model):
    name = models.CharField(max_length=15, blank=True)
    CATEGORY_CHOICES = [
        ('D', 'DogProduct'),
        ('C', 'CumtomProduct'),
        ('N', 'NormalProduct')
    ]
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
    price = models.IntegerField()
    content = models.CharField(max_length=50)
    image = models.ImageField(upload_to='products')
    
    def __str__(self):
        return self.name
    
class UserProducts(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.ForeignKey(PRODUCTS, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user_id', 'product_id')

    def __str__(self):
        r = f'유저 id {self.dog}가 구매한 상품 id {self.number}'
        return r