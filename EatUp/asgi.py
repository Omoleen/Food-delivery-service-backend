"""
ASGI config for EatUp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from .websockets_middleware import JWTAuthMiddleware
from riderapp.routing import url_patterns as rider_urls
from users.routing import url_patterns as user_urls

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EatUp.settings')

# application = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        # Just HTTP for now. (We can add other protocols later.)
        "websocket": JWTAuthMiddleware(URLRouter(rider_urls + user_urls))
    }
)
