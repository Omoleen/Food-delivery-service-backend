from django.urls import path
from .consumers import (MyConsumer,
                        Notifications,
                        VendorRiderOrders
                        )


url_patterns = [
    # path('', MyConsumer.as_asgi()),
    path('notifications/', Notifications.as_asgi()),
    path('orders/', VendorRiderOrders.as_asgi())
]