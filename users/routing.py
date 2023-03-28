from django.urls import path
from .consumers import (MyConsumer,
                        Notifications,
                        Orders
                        )


url_patterns = [
    path('', MyConsumer.as_asgi()),
    path('notifications/', Notifications.as_asgi()),
    path('orders/', Orders.as_asgi())
]