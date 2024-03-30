from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.

class ChatBox(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    receiver = models.IntegerField(default=-1)
    timeStamp = models.DateField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    message = models.TextField()

    def __str__(self):
        return f'payment data - {self.by_restaurant}, dated - {self.timeStamp}'