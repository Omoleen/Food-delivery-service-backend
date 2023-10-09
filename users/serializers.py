from abc import ABC

import requests
from rest_framework.serializers import ModelSerializer, Serializer
from .models import (VerifyPhone,
                     RiderProfile,
                     Rider,
                     Vendor,
                     VendorProfile,
                     VendorEmployee,
                     VendorEmployeeProfile,
                     VendorEmployeePair,
                     Customer,
                     CustomerProfile,
                     Review,
                     BankAccount,
                     Notification,
                     VendorRiderTransactionHistory,
                     User)
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from customerapp.serializers import CustomerDeliveryAddressSerializer
from .utils import generate_ref
from django.conf import settings
from decimal import Decimal


class RegisterPhoneSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    status = serializers.CharField(max_length=100, default='Verification Email/SMS successfully sent', read_only=True)

    class Meta:
        # model = VerifyPhone
        fields = ['phone_number', 'status']

    def validate(self, attrs):
        super().validate(attrs)
        if VerifyPhone.objects.filter(phone_number=attrs.get('phone_number')).exists():
            raise serializers.ValidationError(
                {
                    'phone_number': 'Phone number already exists'
                }
            )
        return attrs

    def create(self, validated_data):
        return VerifyPhone.objects.create(**validated_data)


class VerifyPhoneSerializer(Serializer):
    phone_number = PhoneNumberField(region="NG")
    otp = serializers.CharField(max_length=5, write_only=True)
    status = serializers.CharField(default='success', read_only=True, required=False)

    class Meta:
        fields = ['phone_number', 'otp', 'status']


class PhoneGenerateOTPSerializer(Serializer):
    phone_number = PhoneNumberField(region="NG", write_only=True)
    status = serializers.CharField(default='success', read_only=True, required=False)

    class Meta:
        fields = ['phone_number', 'status']


class PhoneLoginSerializer(Serializer):
    phone_number = PhoneNumberField(region="NG", write_only=True)
    otp = serializers.CharField(max_length=5, write_only=True)
    refresh = serializers.CharField(required=False, read_only=True)
    access = serializers.CharField(required=False, read_only=True)

    class Meta:
        fields = ['phone_number', 'otp']


class RiderProfileSerializer(ModelSerializer):
    class Meta:
        model = RiderProfile
        exclude = ['user', 'id']
        read_only_fields = ['staff_id', 'orders_completed', 'rating', 'borrow_limit', 'borrowed',
                            'amount_earned', 'rider_in_delivery', 'date_allocated', 'period_of_repayment',
                            'cost_of_acquisition', 'return_on_investment', 'bike_type', 'bike_color',
                            'reg_name', 'chasis_num']

    def update(self, instance, validated_data):
        instance.rider_available = validated_data.get('rider_available', instance.rider_available)
        instance.profile_picture_url = validated_data.get('profile_picture_url', instance.profile_picture_url)
        instance.save()
        return instance


class TokenSerializer(serializers.Serializer):
    access = serializers.CharField(max_length=512, read_only=True)
    refresh = serializers.CharField(max_length=512,  read_only=True)

    class Meta:
        exclude = []


class RiderSerializer(ModelSerializer):
    profile = RiderProfileSerializer()
    tokens = TokenSerializer(read_only=True)

    class Meta:
        model = Rider
        exclude = ['id', 'is_superuser', 'is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions', 'role',
                   'otp', 'location']
        # exclude = ['id', 'is_superuser', 'is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions', 'role',
        #            'otp']
        # TODO location
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['wallet', 'date_joined', 'last_login', 'modified_date']

    def validate(self, attrs):
        super().validate(attrs)
        number = PhoneNumber.from_string(attrs['phone_number'])
        phone = VerifyPhone.objects.filter(phone_number=number)
        if phone.exists():
            if not phone[0].is_verified:
                raise serializers.ValidationError(
                    {"phone_number": "phone number has not been verified"})
            if phone[0].user is not None:
                raise serializers.ValidationError(
                    {"phone_number": "phone number is already in use"})
        else:
            raise serializers.ValidationError(
                {"phone_number": "phone number does not exist"})
        return attrs

    def create(self, validated_data):
        phone = VerifyPhone.objects.get(phone_number=validated_data['phone_number'],
                                        is_verified=True,
                                        user=None)
        profile = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        staff_id = str(Rider.objects.all().count() + 1)
        staff_id = 'EU' + ''.join(['0' for _ in range(10 - len(staff_id))]) + staff_id  # generate staff id for riders
        RiderProfile.objects.create(user=instance, staff_id=staff_id, **profile)
        phone.user = instance
        phone.save()
        return instance


class VendorProfileSerializer(ModelSerializer):
    class Meta:
        model = VendorProfile
        exclude = ['user', 'id']
        read_only_fields = ['no_of_orders', 'amount_earned', 'average_star_rating', 'total_rating']

    def update(self, instance, validated_data):
        # if validated_data.get('profile_picture') is not None:
        # instance.profile_picture_url.save(validated_data.get('profile_picture_url').name, validated_data.get('profile_picture_url').file, save=False)
        instance.profile_picture_url = validated_data.get('profile_picture_url', instance.profile_picture_url)
        instance.business_description = validated_data.get('business_description', instance.business_description)
        instance.business_address = validated_data.get('business_address', instance.business_address)
        instance.store_type = validated_data.get('store_type', instance.store_type)
        instance.number_of_stores = validated_data.get('number_of_stores', instance.number_of_stores)
        instance.order_type = validated_data.get('order_type', instance.order_type)
        instance.delivery_type = validated_data.get('delivery_type', instance.delivery_type)
        instance.social_account_1 = validated_data.get('social_account_1', instance.social_account_1)
        instance.social_account_2 = validated_data.get('social_account_2', instance.social_account_2)
        instance.social_account_3 = validated_data.get('social_account_3', instance.social_account_3)
        instance.business_phone_number = validated_data.get('business_phone_number', instance.business_phone_number)
        instance.business_email = validated_data.get('business_email', instance.business_email)
        instance.preparation_time = validated_data.get('preparation_time', instance.preparation_time)
        instance.minimum_order = validated_data.get('minimum_order', instance.minimum_order)
        # instance.profile_picture_url = validated_data.get('profile_picture_url', instance.profile_picture_url)
        instance.open_hour = validated_data.get('open_hour', instance.open_hour)
        instance.close_hour = validated_data.get('close_hour', instance.close_hour)
        instance.save()
        return instance


class VendorSerializer(ModelSerializer):
    profile = VendorProfileSerializer()
    tokens = TokenSerializer(read_only=True)

    class Meta:
        model = Vendor
        exclude = ['id', 'is_superuser', 'is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions', 'role',
                   'otp', 'location']
        # exclude = ['id', 'is_superuser', 'is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions', 'role',
        #            'otp',]
        # TODO location
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['wallet', 'date_joined', 'last_login', 'modified_date', ]

    def validate(self, attrs):
        super().validate(attrs)
        number = PhoneNumber.from_string(attrs['phone_number'])
        phone = VerifyPhone.objects.filter(phone_number=number)
        if phone.exists():
            if not phone[0].is_verified:
                raise serializers.ValidationError(
                    {"phone_number": "phone number has not been verified"})
            if phone[0].user is not None:
                raise serializers.ValidationError(
                    {"phone_number": "phone number is already in use"})
        else:
            raise serializers.ValidationError(
                {"phone_number": "phone number does not exist"})
        return attrs

    def create(self, validated_data):
        phone = VerifyPhone.objects.get(phone_number=validated_data['phone_number'],
                                        is_verified=True,
                                        user=None)
        profile = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        VendorProfile.objects.create(user=instance, **profile)
        phone.user = instance
        phone.save()
        return instance


class VendorEmployeeProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorEmployeeProfile
        exclude = ['id', 'user']


class VendorEmployeeSerializer(serializers.ModelSerializer):
    profile = VendorEmployeeProfileSerializer(read_only=True)
    name = serializers.CharField(max_length=256, write_only=True)
    position = serializers.CharField(max_length=256, write_only=True)
    phone_number = PhoneNumberField()
    wallet_withdrawal = serializers.BooleanField(write_only=True)
    price_change = serializers.BooleanField(write_only=True)
    food_availability = serializers.BooleanField(write_only=True)

    class Meta:
        model = VendorEmployee
        exclude = ['password']

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()
        instance.profile.position = validated_data.get('position', instance.profile.position)
        instance.profile.wallet_withdrawal = validated_data.get('wallet_withdrawal', instance.profile.wallet_withdrawal)
        instance.profile.price_change = validated_data.get('price_change', instance.profile.price_change)
        instance.profile.food_availability = validated_data.get('food_availability', instance.profile.food_availability)
        instance.profile.save()
        return instance

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get('phone_number') is not None:
            if User.objects.filter(phone_number=attrs['phone_number']).exists():
                raise serializers.ValidationError({
                    'phone_number': 'Phone number already exists'
                })
        if attrs.get('name') is not None:
            names = attrs['name'].split(' ')
            if len(names) < 2 or len(names) > 2:
                raise serializers.ValidationError({
                    'name': 'first name and last name needed'
                })
            attrs['first_name'], attrs['last_name'] = names
        return attrs


class VendorEmployeePairSerializer(serializers.ModelSerializer):
    employee = VendorEmployeeSerializer()

    class Meta:
        model = VendorEmployeePair
        exclude = ['id', 'vendor']


class CreateVendorEmployeeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=256)
    position = serializers.CharField(max_length=256)
    phone_number = PhoneNumberField()
    wallet_withdrawal = serializers.BooleanField()
    price_change = serializers.BooleanField()
    food_availability = serializers.BooleanField()
    # password = serializers.CharField(write_only=True)
    # confirmPassword = serializers.CharField(write_only=True)

    class Meta:
        exclude = []

    def create(self, validated_data):

        employee = VendorEmployee.objects.create(first_name=validated_data['first_name'],
                                                 last_name=validated_data['last_name'],
                                                 phone_number=validated_data['phone_number'],
                                                 is_active=True)
        VerifyPhone.objects.create(phone_number=validated_data['phone_number'],
                                   user=employee,
                                   is_verified=True)
        VendorEmployeeProfile.objects.create(user=employee,
                                             position=validated_data['position'],
                                             food_availability=validated_data['food_availability'],
                                             wallet_withdrawal=validated_data['wallet_withdrawal'],
                                             price_change=validated_data['price_change'])
        VendorEmployeePair.objects.create(vendor=self.context['request'].user,
                                          employee=employee)

        return employee

    def validate(self, attrs):
        attrs = super(CreateVendorEmployeeSerializer, self).validate(attrs)
        if User.objects.filter(phone_number=attrs['phone_number']).exists():
            raise serializers.ValidationError({
                'phone_number': 'Phone number already exists'
            })
        # if attrs['password'] != attrs['confirmPassword']:
        #     raise serializers.ValidationError({
        #         'password': 'passwords do not match'
        #     })
        names = attrs['name'].split(' ')
        if len(names) < 2 or len(names) > 2:
            raise serializers.ValidationError({
                'name': 'first name and last name needed'
            })
        attrs['first_name'], attrs['last_name'] = names
        return attrs

    # def update(self, instance, validated_data):
    #     print('update')
    #     instance.first_name = validated_data.get('first_name', instance.first_name)
    #     instance.last_name = validated_data.get('last_name', instance.last_name)
    #     instance.phone_number = validated_data.get('phone_number', instance.phone_number)
    #     instance.save()
    #     instance.profile.position = validated_data.get('position', instance.profile.position)
    #     instance.profile.wallet_withdrawal = validated_data.get('wallet_withdrawal', instance.profile.wallet_withdrawal)
    #     instance.profile.price_change = validated_data.get('price_change', instance.profile.price_change)
    #     instance.profile.food_availability = validated_data.get('food_availability', instance.profile.food_availability)
    #     instance.profile.save()
    #     return instance

    def to_representation(self, instance):
        return VendorEmployeeSerializer(instance).data


class CustomerProfileSerializer(ModelSerializer):
    class Meta:
        model = CustomerProfile
        exclude = ['user', 'id']

    def update(self, instance, validated_data):
        # if validated_data.get('profile_picture') is not None:
        #     instance.profile_picture.save(validated_data.get('profile_picture').name, validated_data.get('profile_picture').file, save=True)
        instance.profile_picture_url = validated_data.get('profile_picture_url', instance.profile_picture_url)
        instance.sms_notification = validated_data.get('sms_notification', instance.sms_notification)
        instance.email_notification = validated_data.get('email_notification', instance.email_notification)
        instance.push_notification = validated_data.get('push_notification', instance.push_notification)
        instance.save()
        return instance


class CustomerSerializer(ModelSerializer):
    profile = CustomerProfileSerializer()
    address = CustomerDeliveryAddressSerializer(many=True, required=False)
    tokens = TokenSerializer(read_only=True)

    class Meta:
        model = Customer
        exclude = ['id', 'is_superuser', 'is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions', 'role',
                   'otp', 'location']
        # exclude = ['id', 'is_superuser', 'is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions', 'role',
        #            'otp',]
        # TODO location
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['wallet', 'date_joined', 'last_login', 'modified_date', 'address']

    def validate(self, attrs):
        super().validate(attrs)
        number = PhoneNumber.from_string(attrs['phone_number'])
        phone = VerifyPhone.objects.filter(phone_number=number)
        if phone.exists():
            if not phone[0].is_verified:
                raise serializers.ValidationError(
                    {"phone_number": "phone number has not been verified"})
            if phone[0].user is not None:
                raise serializers.ValidationError(
                    {"phone_number": "phone number is already in use"})
        else:
            raise serializers.ValidationError(
                {"phone_number": "phone number does not exist"})
        return attrs

    def create(self, validated_data):
        phone = VerifyPhone.objects.get(phone_number=validated_data['phone_number'],
                                        is_verified=True,
                                        user=None)
        profile = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        CustomerProfile.objects.create(user=instance, **profile)
        phone.user = instance
        phone.save()
        return instance


class ReviewSerializer(ModelSerializer):
    reviewer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    receiver_id = serializers.IntegerField()

    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'receiver_id', 'comment', 'rating']
        read_only_fields = ['id', 'reviewer']
        # exclude = ['user', 'id']

    def create(self, validated_data):
        # receiver_id = validated_data.pop('receiver_id')
        instance = self.Meta.model.objects.create(**validated_data)
        return instance


class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        exclude = []


class VerifyAccountDetailsSerializer(serializers.Serializer):
    bank_code = serializers.CharField(max_length=200, )
    account_number = serializers.CharField(max_length=200, )
    account_name = serializers.CharField(max_length=200, read_only=True)
    bank_name = serializers.CharField(max_length=200, read_only=True)
    result = None

    class Meta:
        exclude = ['result']

    def create(self, validated_data):
        return self.result

    def validate(self, attrs):
        super(VerifyAccountDetailsSerializer, self).validate(attrs)
        url = settings.KORAPAY_RESOLVE_API
        payload = {
            'bank': attrs['bank_code'],
            'account': attrs['account_number']
        }
        response = requests.post(url=url, json=payload)
        if response.status_code == 200:
            self.result = response.json()['data']
        else:
            raise serializers.ValidationError({'error': 'Invalid Account'})

        return attrs


class BankAccountSerializer(ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = BankAccount
        fields = '__all__'

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        return instance

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.context['request'].user.bank_accounts.filter(account_number=attrs['account_number']).exists():
            raise serializers.ValidationError({'error': 'Account Number already exists'})
        url = settings.KORAPAY_RESOLVE_API
        payload = {
            'bank': attrs['bank_code'],
            'account': attrs['account_number']
        }
        response = requests.post(url=url, json=payload)
        if response.status_code == 200:
            if not all(item in attrs.items() for item in
                       VerifyAccountDetailsSerializer(response.json()['data']).data.items()):
                raise serializers.ValidationError({
                    'error': 'account details are invalid'
                })
        return attrs

    def update(self, instance, validated_data):
        instance.account_num = validated_data.get('account_num', instance.account_num)
        instance.account_name = validated_data.get('account_name', instance.account_name)
        instance.bank_name = validated_data.get('bank_name', instance.bank_name)
        instance.save()
        return instance


class ListAvailableBanksSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200, )
    # slug = serializers.CharField(max_length=200,)
    code = serializers.CharField(max_length=200, )
    # nibss_bank_code = serializers.CharField(max_length=200,)
    country = serializers.CharField(max_length=200)

    class Meta:
        exclude = []


class VendorRiderTransactionHistorySerializer(ModelSerializer):
    class Meta:
        model = VendorRiderTransactionHistory
        exclude = ['user']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


class WithdrawalSerializer(serializers.Serializer):
    bank_account_id = serializers.IntegerField(write_only=True)
    amount = serializers.FloatField(write_only=True)
    comment = serializers.CharField(max_length=100, allow_null=True, allow_blank=True, write_only=True)
    accounts = None
    transaction = None
    data = VendorRiderTransactionHistorySerializer(read_only=True)

    class Meta:
        exclude = ['bank', 'transaction']

    def create(self, validated_data):
        url = settings.KORAPAY_DISBURSE_API
        self.transaction = VendorRiderTransactionHistory.objects.create(user_id=self.context['user'].vendor.vendor.id if self.context['user'].role == User.Role.VENDOR_EMPLOYEE else self.context['user'].id,
                                                                        title=VendorRiderTransactionHistory.TransactionTypes.PAYOUT,
                                                                        comment=validated_data['comment'],
                                                                        amount=validated_data['amount'],
                                                                        transaction_id=generate_ref())

        payload = {
            "reference": self.transaction.transaction_id,
            "destination": {
                "type": "bank_account",
                "amount": validated_data['amount'],
                "currency": "NGN",
                "narration": "Test Transfer Payment",
                "bank_account": {
                    "bank": self.accounts[0].bank_code,
                    "account": self.accounts[0].account_number
                },
                "customer": {
                    "email": self.context['user'].vendor.vendor.email if self.context['user'].role == User.Role.VENDOR_EMPLOYEE else self.context['user'].email
                }
            }
        }
        headers = {
            'Authorization': f'Bearer {settings.KORAPAY_SECRET_KEY}'
        }
        response = requests.post(url=url, json=payload, headers=headers)
        if response.status_code == 200:
            if response.json()['data']['status'] == 'processing':
                self.context['user'].wallet -= Decimal(validated_data['amount'])
                self.context['user'].save()
                return self.transaction
        self.transaction.transaction_status = VendorRiderTransactionHistory.TransactionStatus.FAILED
        self.transaction.save()
        return self.transaction

    def validate(self, attrs):
        super().validate(attrs)
        if self.context['user'].role == User.Role.VENDOR_EMPLOYEE:
            if not self.context['user'].profile.wallet_withdrawal:
                raise serializers.ValidationError({
                    'permissions': "You don't have this permission"
                })
            self.accounts = self.context['user'].vendor.vendor.bank_accounts.filter(id=attrs['bank_account_id'])
        else:
            self.accounts = self.context['user'].bank_accounts.filter(id=attrs['bank_account_id'])
        if not self.accounts.exists():
            raise serializers.ValidationError({'bank_account_id': 'Bank Account id does not exist'})
        if self.context['user'].wallet < attrs['amount']:
            raise serializers.ValidationError({'amount': 'withdrawal amount is greater than the wallet balance'})
        if attrs['amount'] < 500:
            raise serializers.ValidationError({'amount': 'Minimum withdrawal amount is 500 naira'})
            # TODO minimum withdrawal amount

        return attrs

    def to_representation(self, instance):
        representation = {
            'data': VendorRiderTransactionHistorySerializer(self.transaction).data
        }
        representation['data']['amount'] = Decimal(representation['data']['amount'])
        return representation


class UpdateLocationViewSerializer(Serializer):
    location_lat = serializers.FloatField()
    location_long = serializers.FloatField()

    class Meta:
        exclude = []

    def create(self, validated_data):
        self.context['request'].user.location_lat = validated_data['location_lat']
        self.context['request'].user.location_long = validated_data['location_long']
        self.context['request'].user.save()
        return self.context['request'].user


