from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class ChatBox(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', null=False)
    receiver = models.IntegerField(default=-1, null=False)
    timeStamp = models.DateField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    message = models.TextField()
    room = models.CharField(max_length=20, default='1-2')

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.message}"


class Demand(models.Model):
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=300)
    category = models.CharField(max_length=200)
    description = models.TextField(default='')
    price = models.IntegerField(default=0)
    image = models.ImageField(upload_to='demands/images', null=True, blank=True)
    available = models.BooleanField(default=True)
    timeStamp = models.DateField(auto_now_add=True)
    feedback = models.IntegerField(default=0)

class Offering(models.Model):
    lender = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=300)
    category = models.CharField(max_length=200)
    description = models.TextField(default='')
    price = models.IntegerField(default=0)
    image = models.ImageField(upload_to='offerings/images', null=True, blank=True)
    available = models.BooleanField(default=True)
    timeStamp = models.DateField(auto_now_add=True)
    feedback = models.IntegerField(default=0)

class Deal(models.Model):
    lender = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    borrower = models.IntegerField(null=False)
    item = models.ForeignKey(Offering, on_delete=models.CASCADE, null=False)
    price = models.IntegerField(default=0)
    timeStamp = models.DateField(auto_now_add=True)
    feedback = models.TextField(default='')
    item_returned = models.BooleanField(default=False)


class Grievance(models.Model):
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, null=True)
    count = models.IntegerField(default=0)
    subject = models.CharField(max_length=100, default='Item damage')
    description = models.TextField(default='')
    resolved = models.BooleanField(default=False)
    timeStamp = models.DateField(auto_now_add=True)
    faulty_item_image = models.ImageField(upload_to='grievances/images', null=True, blank=True)


class Notification(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
    associated_url = models.URLField(default='/')
    about = models.TextField(default='Notification')

