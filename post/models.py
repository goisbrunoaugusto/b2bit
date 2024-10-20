from django.db import models
from account.models import UserData

class Post(models.Model):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(UserData, related_name='like', blank=True)

    def likes_count(self):
        return self.like.count()

    def __str__(self):
        return self.content