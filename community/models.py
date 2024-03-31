from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class ChatBox(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.IntegerField(default=-1)
    timeStamp = models.DateField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    message = models.TextField()

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.message}"
