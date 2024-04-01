from django.contrib import admin
from .models import ChatBox, Demand, Offering, Deal, Grievance, Notification

# Register your models here.

admin.site.register(ChatBox)
admin.site.register(Demand)
admin.site.register(Offering)
admin.site.register(Deal)
admin.site.register(Grievance)
admin.site.register(Notification)
