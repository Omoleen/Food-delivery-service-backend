from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from users.models import (Vendor, VendorProfile, Customer)
from customerapp.models import CustomerDeliveryAddress
import string
import random


# MENU - START -
class MenuCategory(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.vendor} - {self.name} Category'

    class Meta:
        unique_together = ('vendor', 'name',)


class MenuItem(models.Model):

    class QuantityType(models.TextChoices):
        PER_WRAP = "PER_WRAP", 'Per Wrap'
        PER_SPOON = "PER_SPOON", 'Per Spoon'
        PER_PLATE = "PER_PLATE", 'Per Plate'

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_menu_items')
    name = models.CharField(max_length=64)
    summary = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, null=True)
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items', null=True)
    quantity = models.CharField(max_length=64, choices=QuantityType.choices, null=True)
    image = models.ImageField(upload_to='vendor/menu_item/%Y/%m/%d', blank=True, null=True)

    def __str__(self):
        return f'{self.category} - {self.name} item'

    class Meta:
        unique_together = ('category', 'name',)


class MenuSubItem(models.Model):
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='subitems')
    name = models.CharField(max_length=64)
    max_items = models.IntegerField(default=0)  # max number of items a user can pick from a sub item
    items = models.JSONField(default=list)

    def __str__(self):
        return f'{self.item} - {self.name} sub item'

    class Meta:
        unique_together = ('item', 'name',)

# MENU - END -


class VendorTransactionHistory(models.Model):

    class QuantityType(models.TextChoices):
        PAYOUT = "PAYOUT", 'payout'
        INCOME = "INCOME", 'income'

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=54, null=True, blank=True)
    comment = models.CharField(max_length=54, null=True, blank=True)
    under_review = models.DateTimeField(auto_now=True)


class Order(models.Model):
    class OrderType(models.TextChoices):
        PICKUP = "PICKUP", 'pickup'
        DELIVERY = "DELIVERY", 'delivery'

    class PaymentMethod(models.TextChoices):
        WEB = "WEB", 'web'
        WALLET = "WALLET", 'wallet'
        WEB_WALLET = 'WEB_WALLET', 'web wallet'

    class StatusType(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Requested'
        CANCELLED = 'CANCELLED', 'Cancelled'
        ON_DELIVERY = 'ON_DELIVERY', 'On Delivery'
        DELIVERED = 'DELIVERED', 'Delivered'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'

    class DeliveryPeriodTypes(models.TextChoices):
        NOW = 'NOW', 'now'
        LATER = 'LATER', 'later'

    id = models.CharField(primary_key=True, max_length=64)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='customer_orders')
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name='vendor_order')
    type = models.CharField(choices=OrderType.choices, max_length=20)
    delivery_address = models.TextField(null=True)
    location = models.CharField(max_length=50, null=True)
    delivery_period = models.CharField(max_length=50, choices=DeliveryPeriodTypes.choices, default=DeliveryPeriodTypes.NOW)
    later_time = models.DateTimeField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True)
    payment_method = models.CharField(choices=PaymentMethod.choices, null=True, max_length=20)
    third_party_name = models.CharField(max_length=100, null=True)
    note = models.TextField(null=True)
    delivery_fee = models.FloatField(null=True)
    vat = models.FloatField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=StatusType.choices, default=StatusType.REQUESTED)

    def save(self, *args, **kwargs):
        alphabets = string.ascii_letters
        numbers = string.digits
        available = alphabets + numbers
        if not self.id or self.id is None:
            self.id = '#'+''.join(random.choices(available, k=6)) + 'EU'
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Order no. - {self.id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='orders')
    choice = models.JSONField(null=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} - {self.item} - {self.choice}'
