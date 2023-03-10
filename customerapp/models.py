from django.db import models
from users.models import Customer, CustomerProfile, User
# Create your models here.


class CustomerDeliveryAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_addresses')
    number = models.IntegerField(null=True)
    address = models.TextField(null=True)
    landmark = models.CharField(max_length=50, null=True)
    label = models.CharField(max_length=50)

    class Meta:
        unique_together = ('customer', 'label')

    def __str__(self):
        return f'{self.customer} - {self.label}'


class CustomerTransactionHistory(models.Model):
    class TransactionTypes(models.TextChoices):
        FOOD_PURCHASE = 'FOOD PURCHASE', 'Food Purchase'
        REFUND = 'REFUND', 'Refund'
        WEB_TOP_UP = 'WEB TOP UP', 'Web Top Up'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_transactions')
    title = models.CharField(max_length=100, choices=TransactionTypes.choices, blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    transaction_id = models.CharField(max_length=100, default='', blank=True, null=True)
    delivery_id = models.CharField(max_length=100, default='', blank=True, null=True)
    restaurant = models.CharField(max_length=100, default='', blank=True, null=True)
    payment_method = models.CharField(max_length=100, default='', blank=True, null=True)

    def __str__(self):
        return f'{self.title} - {self.date_time}'
