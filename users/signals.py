from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from django.dispatch import receiver
from .models import *


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