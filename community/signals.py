from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ChatBox
from  django.contrib.auth.models import User

@receiver(post_save, sender=ChatBox)
def on_model_update(sender, instance, created, **kwargs):
    if created:
        user1 = instance.sender
        user2 = User.objects.filter(id=instance.receiver)[0]
        
        # Check if a chat room already exists between these users
        existing_room = ChatRoom.objects.filter(user1=user1, user2=user2)
        if not existing_room.exists():
            ChatRoom.objects.create(user1=user1, user2=user2)

    channel_layer = get_channel_layer()
    group_name = "chat_%s" % instance.receiver

    # Send message to WebSocket group
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_chat',
            'message': instance.message,  # Customize the message
        }
    )


