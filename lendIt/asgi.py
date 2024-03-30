import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lendIt.settings')

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter , URLRouter
from community import routing

application = ProtocolTypeRouter(
    {
        "http" : get_asgi_application() , 
        "websocket" : AuthMiddlewareStack(
            URLRouter(
                routing.websocket_urlpatterns
            )    
        )
    }
)
