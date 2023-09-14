from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from django.dispatch import receiver
from .models import *
from .tasks import delete_unverified_user


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
def send_otp_on_create(sender, instance, created, **kwargs):
    if instance.is_paid:
        vendor_orders = instance.vendors.all()
        for vendor in vendor_orders:
            if not vendor.is_paid:
                vendor.is_paid = True
                vendor.save()
