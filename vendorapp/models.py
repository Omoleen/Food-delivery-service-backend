from django.db import models
from users.models import (Vendor, VendorProfile, Customer, Rider)
from customerapp.models import CustomerDeliveryAddress
from django.contrib.auth.models import Group


class VendorTransactionHistory(models.Model):

    class QuantityType(models.TextChoices):
        PAYOUT = "PAYOUT", 'payout'
        INCOME = "INCOME", 'income'

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_transactions')
    date = models.DateTimeField(auto_now_add=True)
    user = models.CharField(max_length=54, null=True, blank=True)
    comment = models.CharField(max_length=54, null=True, blank=True)
    under_review = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.vendor} - {self.date}'


