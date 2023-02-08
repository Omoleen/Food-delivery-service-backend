from django.db import models
from users.models import Customer, CustomerProfile, User
# Create your models here.


class CustomerDeliveryAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    number = models.IntegerField(null=True)
    address = models.TextField(null=True)
    landmark = models.CharField(max_length=50, null=True)
    label = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.customer} - {self.label}'
