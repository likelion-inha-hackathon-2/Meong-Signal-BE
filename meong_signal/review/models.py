from django.db import models
from account.models import User
from dog.models import Dog
from django.core.validators import MinValueValidator, MaxValueValidator

class UserReview(models.Model):
    evaluated_user_id = models.ForeignKey(User, related_name="user_reviews_received", on_delete=models.CASCADE) # 리뷰받은 사람의 id
    evaluator_id = models.ForeignKey(User, related_name="user_reviews_given", on_delete=models.CASCADE) # 리뷰남긴 사람의 id
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.CharField(max_length=50)

class WalkingReview(models.Model):
    evaluated_user_id = models.ForeignKey(User, related_name="walk_reviews_received", on_delete=models.CASCADE) # 리뷰받은 사람의 id
    evaluator_id = models.ForeignKey(User, related_name="walk_reviews_given", on_delete=models.CASCADE) # 리뷰남긴 사람의 id
    dog_id = models.ForeignKey(Dog, on_delete=models.CASCADE) # 같이 산책한 강아지의 id
    content = models.CharField(max_length=50)

class ReviewTag(models.Model):
    review_id = models.ForeignKey(WalkingReview, on_delete=models.CASCADE)
    dog_id = models.ForeignKey(Dog, on_delete=models.CASCADE) # 같이 산책한 강아지의 id
    number = models.IntegerField()