from django.db import models

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