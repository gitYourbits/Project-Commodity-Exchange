from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<receiver_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/group/(?P<group_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
