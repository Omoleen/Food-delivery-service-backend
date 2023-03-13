from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from django.dispatch import receiver
from .models import *


# @receiver(pre_save, sender=RiderLoan)
def create_loan_payments(sender, instance, **kwargs):
    print(kwargs)
    # if instance

