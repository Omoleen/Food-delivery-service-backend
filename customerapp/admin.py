from django.contrib import admin
from .models import (CustomerDeliveryAddress,
                     CustomerTransactionHistory)
# Register your models here.

admin.site.register(CustomerDeliveryAddress)
admin.site.register(CustomerTransactionHistory)
