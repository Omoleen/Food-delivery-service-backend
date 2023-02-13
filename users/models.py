from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin,
                                        AbstractUser)
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from .utils import generate_code
import uuid
import string
import random
# from customerapp.models import CustomerDeliveryAddress
# from vendorapp.models import MenuItem


class CustomUserManager(BaseUserManager):

    def create_user(self, first_name, last_name, phone_number, role, username, email, password=None, *args, **kwargs):

        if not email:
            raise ValueError('User must have an email address')

        if not phone_number:
            raise ValueError("User must have a phone number")

        if not username:
            raise ValueError('User must have an username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone_number=phone_number,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password=None, **kwargs):
        if password is None:
            raise TypeError('Password should not be none')

        if not email:
            raise ValueError('User must have an email address')

        if not phone_number:
            raise ValueError("User must have a phone number")

        kwargs.update({'is_superuser': True,
                       'is_staff': True,
                       'is_admin': True})

        user = self.model(
            email=self.normalize_email(email),
            phone_number=phone_number,
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", 'Admin'
        RIDER = "RIDER", 'Rider'
        VENDOR = "VENDOR", 'Vendor'
        CUSTOMER = "CUSTOMER", 'Customer'
        VENDORUSER = "VENDORUSER", 'VendorUser'
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = PhoneNumberField(unique=True)
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.ADMIN)
    wallet = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    city = models.CharField(max_length=50, blank=True, null=True)

    # required fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    modified_date = models.DateTimeField(auto_now=True)

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class RiderManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.RIDER)


class Rider(User):
    objects = RiderManager()
    base_role = User.Role.RIDER

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.id or self.id is None:
            self.role = self.base_role
        return super().save(*args, **kwargs)

    @property
    def profile(self):
        return self.riderprofile


class RiderProfile(models.Model):
    user = models.OneToOneField(Rider, on_delete=models.CASCADE)
    staff_id = models.CharField(max_length=64, unique=True)
    profile_picture = models.ImageField(upload_to='rider/profile_pictures/%Y/%m/%d', blank=True, null=True)
    orders_completed = models.IntegerField(default=0)
    rider_available = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

#     Motorcycle details
    date_allocated = models.DateField(null=True, blank=True)
    period_of_repayment = models.FloatField(null=True, blank=True)
    cost_of_acquisition = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    return_on_investment = models.FloatField(null=True, blank=True)
    bike_type = models.CharField(max_length=64, null=True, blank=True)
    bike_color = models.CharField(max_length=64, null=True, blank=True)
    reg_name = models.CharField(max_length=64, null=True, blank=True)
    chasis_num = models.CharField(max_length=64, null=True, blank=True)

    def __str__(self):
        return f'{self.user} profile'


class VendorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.VENDOR)


class Vendor(User):
    objects = VendorManager()
    base_role = User.Role.VENDOR

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.id or self.id is None:
            self.role = self.base_role
        return super().save(*args, **kwargs)

    @property
    def profile(self):
        return self.vendorprofile


class VendorProfile(models.Model):

    class StoreType(models.TextChoices):
        INSTANT = "INSTANT", 'instant'
        BATCHES = "BATCHES", 'batches'
        PREORDER = "PREORDER", 'preorder'

    class OrderType(models.TextChoices):
        PICKUP = "PICKUP", 'pickup'
        DELIVERY = "DELIVERY", 'delivery'
        PICKUP_AND_DELIVERY = "PICKUP_AND_DELIVERY", 'pickup_and_delivery'

    class DeliveryType(models.TextChoices):
        PERSONAL_RIDERS = "PERSONAL_RIDERS", 'personal_riders'
        PERSONAL_RIDERS_AND_EU_HEROES = "PERSONAL_RIDERS_AND_EU_HEROES", 'personal_riders_and_eu_heroes'
        EU_HEROES = "EU_HEROES", 'eu_heroes'

    user = models.OneToOneField(Vendor, on_delete=models.CASCADE)
    user_rank = models.CharField(max_length=64, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='vendor/profile_pictures/%Y/%m/%d', blank=True, null=True)
    business_name = models.CharField(max_length=64, blank=True, null=True)
    business_description = models.TextField(blank=True, null=True)
    business_address = models.CharField(max_length=64, blank=True, null=True)
    store_type = models.CharField(max_length=64, choices=StoreType.choices, blank=True, null=True)
    number_of_stores = models.IntegerField(blank=True, null=True)
    order_type = models.CharField(max_length=64, choices=OrderType.choices, blank=True, null=True)
    delivery_type = models.CharField(max_length=64, choices=DeliveryType.choices, blank=True, null=True)
    social_account_1 = models.URLField(blank=True, null=True)
    social_account_2 = models.URLField(blank=True, null=True)  # change to jsonfield
    social_account_3 = models.URLField(blank=True, null=True)
    business_phone_number = PhoneNumberField(blank=True)
    business_email = models.EmailField(_('business email address'), unique=True, blank=True, null=True)
    preparation_time = models.IntegerField(blank=True, null=True)  # in minutes
    minimum_order = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.user} profile'


class CustomerManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.CUSTOMER)


class Customer(User):
    objects = CustomerManager()
    base_role = User.Role.CUSTOMER

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.id or self.id is None:
            self.role = self.base_role
        return super().save(*args, **kwargs)

    @property
    def profile(self):
        return self.customerprofile


class CustomerProfile(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='vendor/profile_pictures/%Y/%m/%d', blank=True, null=True)
    sms_notification = models.BooleanField(default=False)
    email_notification = models.BooleanField(default=False)
    push_notification = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user} profile'


class VendorEmployeesManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.VENDORUSER)


class VendorEmployee(User):

    objects = VendorEmployeesManager()
    base_role = User.Role.VENDORUSER

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.id or self.id is None:
            self.role = self.base_role
            self.is_active = True
            self.wallet = None
        return super().save(*args, **kwargs)


class VendorEmployeeProfile(models.Model):
    user = models.OneToOneField(VendorEmployee, on_delete=models.CASCADE, related_name='vendor_employee_profile')
    app_access = {
        'wallet_withdrawal': False,
        'price_change': False,
        'food_availability': True
    }
    position = models.CharField(max_length=54)
    App_Access = models.JSONField(default=dict)

    def __str__(self):
        return f'{self.user} profile'


class VendorEmployeePair(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='employee')
    employee = models.ForeignKey(VendorEmployee, on_delete=models.CASCADE, related_name='vendor')


class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_num = models.CharField(max_length=64)
    account_name = models.CharField(max_length=64)
    bank_name = models.CharField(max_length=64)


class VerifyPhone(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, default=None)
    phone_number = PhoneNumberField(unique=True)
    otp = models.IntegerField()
    is_verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.phone_number)

    def save(self, *args, **kwargs):
        if not self.id or self.id is None:
            self.otp = generate_code()
            print(self.otp)
            # input code to send email or text to verify and call worker
            # to delete from table if phone number has not been verified
            # after 30 minutes
        return super().save(*args, **kwargs)


class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comment')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reviews')
    comment = models.TextField()
    rating = models.FloatField()


# class Order(models.Model):
#     class OrderType(models.TextChoices):
#         PICKUP = "PICKUP", 'pickup'
#         DELIVERY = "DELIVERY", 'delivery'
#
#     class PaymentMethod(models.TextChoices):
#         WEB = "WEB", 'web'
#         WALLET = "WALLET", 'wallet'
#
#     id = models.CharField(primary_key=True, max_length=64)
#     customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='customer_order')
#     vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name='vendor_order')
#     type = models.CharField(choices=OrderType.choices, max_length=20)
#     delivery_address = models.TextField(null=True)
#     phone_number = PhoneNumberField(null=True)
#     payment_method = models.CharField(choices=PaymentMethod.choices, null=True, max_length=20)
#     third_party_name = models.CharField(max_length=100, null=True)
#     note = models.TextField(null=True)
#     delivery_fee = models.FloatField()
#     vat = models.FloatField()
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#     # delivery_address = models.TextField(null=True)
#
#     def save(self, *args, **kwargs):
#         alphabets = string.ascii_letters
#         numbers = string.digits
#         available = alphabets + numbers
#         if not self.id or self.id is None:
#             self.id = '#'.join(random.choices(available, k=6)) + 'EU'
#         return super().save(*args, **kwargs)
#
#     def __str__(self):
#         return f'Order no. - {self.id}'


# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
#     item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, related_name='')
