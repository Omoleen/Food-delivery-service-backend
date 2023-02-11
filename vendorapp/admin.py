from django.contrib import admin
from .models import (MenuCategory,
                     MenuItem,
                     MenuSubItem,
                     VendorTransactionHistory,
                     Order,
                     OrderItem)

# Register your models here.
admin.site.register(MenuCategory)
admin.site.register(MenuItem)
admin.site.register(MenuSubItem)
admin.site.register(VendorTransactionHistory)
admin.site.register(Order)
admin.site.register(OrderItem)
