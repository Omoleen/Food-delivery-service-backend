"""
ASGI config for EatUp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EatUp.settings')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from riderapp.routing import url_patterns as rider_urls
from users.routing import url_patterns as user_urls
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        # Just HTTP for now. (We can add other protocols later.)
        "websocket": AuthMiddlewareStack(
            AllowedHostsOriginValidator(
                URLRouter(rider_urls + user_urls)
            )
        )
    }
)
