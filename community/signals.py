# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
# from .models import ChatBox

# @receiver(post_save, sender=ChatBox)
# def on_model_update(sender, instance, created, **kwargs):
#     if created:
#         channel_layer = get_channel_layer()
#         group_name = "notification_%s" % instance.sender

#         # Send message to WebSocket group
#         async_to_sync(channel_layer.group_send)(
#             group_name,
#             {
#                 'type': 'send_notification',
#                 'message': 'new order arrived!',  # Customize the message
#             }
#         )


#     else:
#         channel_layer = get_channel_layer()
#         group_name = "notification_%s" % instance.ordered_by

#         order_id = instance.order_id

#         # Send message to WebSocket group
#         async_to_sync(channel_layer.group_send)(
#             group_name,
#             {
#                 'type': 'send_notification',
#                 'message': order_id,  # Customize the message
#             }
#         )


