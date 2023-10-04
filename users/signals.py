from decimal import Decimal

from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from django.dispatch import receiver
from .models import *
from .tasks import delete_unverified_user, send_push_message


# @receiver(post_save, sender=User)
def create_rider_profile(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.RIDER:
        staff_id = str(Rider.objects.all().count() + 1)
        staff_id = 'EU' + ''.join(['0' for _ in range(10-len(staff_id))]) + staff_id  # generate staff id for riders
        RiderProfile.objects.create(user=instance, staff_id=staff_id)


@receiver(post_save, sender=VerifyPhone)
def send_otp_on_create(sender, instance, created, **kwargs):
    if created:
        instance.send_code(created=True)
        phone_number = str(instance.phone_number)
        delete_unverified_user.apply_async([phone_number], countdown=700)


@receiver(post_save, sender=CustomerOrder)
def update_vendor_orders_after_payment(sender, instance, created, **kwargs):
    if instance.is_paid:
        vendor_orders = instance.vendors.all()
        for vendor_order in vendor_orders:
            if not vendor_order.is_paid:
                vendor_order.vendor.wallet += vendor_order.amount
                vendor_order.vendor.save()
                vendor_order.is_paid = True
                vendor_order.save()
                vendor_order.vendor.notifications.create(
                    title='New Order!',
                    content=f"You have a new order {instance}"
                )

@receiver(post_save, sender=VendorOrder)
def order_notification(sender, instance, created, **kwargs):
    pass

@receiver(post_save, sender=CustomerTransactionHistory)
def customer_transaction_history(sender, instance, created, **kwargs):
    pass

@receiver(post_save, sender=VendorRiderTransactionHistory)
def vendor_rider_transaction_history(sender, instance, created, **kwargs):
    pass

@receiver(post_save, sender=Notification)
def send_push_notifications(sender, instance: Notification, created, **kwargs):
    send_push_message.delay(instance.content, instance.title, instance.user.notification_id)

