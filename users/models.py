import datetime

from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin,
                                        AbstractUser)
# from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db.models.functions import Distance
# from vendorapp.models import Order
# from vendorapp.models import MenuItem
from .utils import generate_code
import uuid
import string
import random
# from customerapp.models import CustomerDeliveryAddress
# from vendorapp.models import MenuItem
from rest_framework_simplejwt.tokens import RefreshToken
from .tasks import send_otp_sms, change_code


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
    otp = models.IntegerField(default=0000)
    location = models.PointField(null=True, blank=True, srid=4326)
    location_lat = models.FloatField(null=True, blank=True, default=0)
    location_long = models.FloatField(null=True, blank=True, default=0)
    # registration_id = models.CharField(_('device token'), max_length=128)

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

    def save(self, *args, **kwargs):
        self.location = Point(float(self.location_long), float(self.location_lat))
        return super().save(*args, **kwargs)


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
    amount_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rider_available = models.BooleanField(default=False)
    rider_in_delivery = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    borrowed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    borrow_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

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
    no_of_orders = models.IntegerField(default=0)
    amount_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    average_star_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_rating = models.IntegerField(default=0)

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
    profile_picture = models.ImageField(upload_to='customer/profile_pictures/%Y/%m/%d', blank=True, null=True)
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

    @property
    def profile(self):
        return self.vendoremployeeprofile


class VendorEmployeeProfile(models.Model):
    user = models.OneToOneField(VendorEmployee, on_delete=models.CASCADE)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    account_number = models.CharField(max_length=64, default='')
    account_name = models.CharField(max_length=64, default='')
    bank_name = models.CharField(max_length=64, default='')
    bank_code = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.user} Bank Account'

    class Meta:
        unique_together = ('user', 'account_number')


class VerifyPhone(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, default=None)
    phone_number = PhoneNumberField(unique=True)
    otp = models.CharField(max_length=64)
    is_verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.phone_number)

    def generate_code(self, n=True):
        self.otp = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        print(self.otp)
        self.save()
        if n:
            change_code.apply_async(args=[str(self.phone_number), self.otp], countdown=600)
        return self.otp

    def send_code(self, created=False):
        self.generate_code()
        send_otp_sms.delay(str(self.phone_number)[1:], self.otp, created)

    def get_tokens_for_user(self):
        refresh = RefreshToken.for_user(self.user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


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
    availability = models.BooleanField(null=True, blank=True, default=True)
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


# ORDER - START -
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
        READY = 'READY', 'Ready'
        DELIVERED = 'DELIVERED', 'Delivered'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'

    class DeliveryPeriodTypes(models.TextChoices):
        NOW = 'NOW', 'now'
        LATER = 'LATER', 'later'

    id = models.CharField(primary_key=True, max_length=64)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='customer_orders')
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, related_name='vendor_orders')
    rider = models.ForeignKey(Rider, on_delete=models.SET_NULL, null=True, related_name='rider_orders')
    type = models.CharField(choices=OrderType.choices, max_length=20, default=OrderType.DELIVERY)
    delivery_address = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=50, null=True, blank=True)
    delivery_period = models.CharField(max_length=50, choices=DeliveryPeriodTypes.choices, default=DeliveryPeriodTypes.NOW)
    later_time = models.DateTimeField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    payment_method = models.CharField(choices=PaymentMethod.choices, null=True, max_length=20, blank=True)
    third_party_name = models.CharField(max_length=100, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    delivery_fee = models.FloatField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    pickup_time = models.TimeField(null=True, blank=True)
    delivered_time = models.TimeField(null=True, blank=True)
    vat = models.FloatField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=StatusType.choices, default=StatusType.REQUESTED)
    total = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        alphabets = string.ascii_letters
        numbers = string.digits
        available = alphabets + numbers
        if not self.id or self.id is None:
            self.id = ''.join(random.choices(available, k=7)) + 'EU'
        else:
            self.check_pickup_time_and_delivery_time()
        if not self.total:
            #TODO calculate total
            print('calculate total order')
        return super().save(*args, **kwargs)

    def check_pickup_time_and_delivery_time(self):
        # check if a new db row is being added
        # When this happens the `_loaded_values` attribute will not be available
        if not self._state.adding:
            # check if field_1 is being updated
            if self._loaded_values['status'] == self.StatusType.IN_PROGRESS and self.status == self.StatusType.ON_DELIVERY:
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print('save pick up time')
                self.pickup_time = current_time
            elif self._loaded_values['status'] == self.StatusType.ON_DELIVERY and self.status == self.StatusType.DELIVERED:
                now = datetime.datetime.now()
                current_time = now.strftime("%H:%M:%S")
                print('save pick up time')
                self.delivered_time = current_time

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)

        # save original values, when model is loaded from database,
        # in a separate attribute on the model
        instance._loaded_values = dict(zip(field_names, values))

        return instance

    def __str__(self):
        return f'Order no. - {self.id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', null=True)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='orders')
    choice = models.JSONField(null=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} - {self.item} - {self.choice}'
# ORDER - END -


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
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=64, null=True, blank=True)
    button_text = models.CharField(max_length=64, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.title}'


class AboutEatup(models.Model):
    phone_number = PhoneNumberField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)

    def __str__(self):
        return 'About Eatup'


class WebhooksPaymentMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    message = models.JSONField(default=dict)
    date_created = models.DateTimeField(auto_now_add=True)
    event = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    reference = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.event} {self.status}'


class VendorRiderTransactionHistory(models.Model):
    class TransactionTypes(models.TextChoices):
        PAYOUT = "PAYOUT", 'payout'
        INCOME = "INCOME", 'income'

    class TransactionStatus(models.TextChoices):
        PROCESSING = 'PROCESSING', 'Processing'
        FAILED = 'FAILED', 'Failed'
        SUCCESS = 'SUCCESS', 'Success'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=100, choices=TransactionTypes.choices, blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=54, null=True, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    transaction_id = models.CharField(max_length=100, default='', blank=True, null=True, help_text='reference')
    payment_method = models.CharField(max_length=100, default='Bank Account', blank=True, null=True)
    transaction_status = models.CharField(max_length=100,
                                          default=TransactionStatus.PROCESSING,
                                          choices=TransactionStatus.choices)

    def __str__(self):
        return f'{self.title} - {self.date_time}'
