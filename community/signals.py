from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import ChatBox

@receiver(post_save, sender=ChatBox)
def on_model_update(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        group_name = f"chat_{instance.room}"

        message_payload = {
            'id': instance.id,
            'message': instance.message,
            'sender_id': instance.sender.id,
            'receiver_id': instance.receiver,
        }

        # Send message to WebSocket group
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_message',
                'message': message_payload,  # Customize the message
            }
        )
