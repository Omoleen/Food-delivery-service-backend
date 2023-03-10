from rest_framework.serializers import ModelSerializer, Serializer
from .models import (VerifyPhone,
                     RiderProfile,
                     Rider,
                     Vendor,
                     VendorProfile,
                     Customer,
                     CustomerProfile,
                     Review,
                     BankAccount,
                     Notification)
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from customerapp.serializers import CustomerDeliveryAddressSerializer


class RegisterPhoneSerializer(ModelSerializer):

    class Meta:
        model = VerifyPhone
        fields = ['phone_number']
        extra_kwargs = {
            'phone_number': {'write_only': True}
        }

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
        #TODO send OTP to user
        return self.Meta.model.objects.create(**validated_data)


class VerifyPhoneSerializer(Serializer):
    phone_number = PhoneNumberField(region="NG", write_only=True)
    otp = serializers.IntegerField(write_only=True)

    class Meta:
        fields = ['phone_number', 'otp']
        extra_kwargs = {
            'phone_number': {'write_only': True},
            'otp': {'write_only': True}
        }


class PhoneGenerateOTPSerializer(Serializer):
    phone_number = PhoneNumberField(region="NG", write_only=True)
    status = serializers.CharField(default='success', read_only=True, required=False)

    class Meta:
        fields = ['phone_number', 'status']


class PhoneLoginSerializer(Serializer):
    phone_number = PhoneNumberField(region="NG", write_only=True)
    otp = serializers.IntegerField(write_only=True)
    refresh = serializers.CharField(required=False, read_only=True)
    access = serializers.CharField(required=False, read_only=True)

    class Meta:
        fields = ['phone_number', 'otp']


class RiderProfileSerializer(ModelSerializer):

    class Meta:
        model = RiderProfile
        exclude = ['user', 'id']
        read_only_fields = ['staff_id', 'orders_completed', 'rating', 'rider_available']

    def update(self, instance, validated_data):
        instance.rider_available = validated_data.get('rider_available', instance.rider_available)
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.save()
        return instance


class RiderSerializer(ModelSerializer):
    profile = RiderProfileSerializer()

    class Meta:
        model = Rider
        exclude = ['id', 'is_superuser', 'is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions', 'role', 'otp']
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
        staff_id = 'EU' + ''.join(['0' for _ in range(10-len(staff_id))]) + staff_id  # generate staff id for riders
        RiderProfile.objects.create(user=instance, staff_id=staff_id,  **profile)
        phone.user = instance
        phone.save()
        return instance


class VendorProfileSerializer(ModelSerializer):

    class Meta:
        model = VendorProfile
        exclude = ['user', 'id']

    def update(self, instance, validated_data):
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
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
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.save()
        return instance


class VendorSerializer(ModelSerializer):
    profile = VendorProfileSerializer()

    class Meta:
        model = Vendor
        exclude = ['id', 'is_superuser', 'is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions', 'role', 'otp']
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ['wallet', 'date_joined', 'last_login', 'modified_date',]

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
        VendorProfile.objects.create(user=instance,  **profile)
        phone.user = instance
        phone.save()
        return instance


class CustomerProfileSerializer(ModelSerializer):

    class Meta:
        model = CustomerProfile
        exclude = ['user', 'id']

    def update(self, instance, validated_data):
        instance.profile_picture = validated_data.get('profile_picture', instance.profile_picture)
        instance.sms_notification = validated_data.get('sms_notification', instance.sms_notification)
        instance.email_notification = validated_data.get('email_notification', instance.email_notification)
        instance.push_notification = validated_data.get('push_notification', instance.push_notification)
        instance.save()
        return instance


class CustomerSerializer(ModelSerializer):
    profile = CustomerProfileSerializer()
    address = CustomerDeliveryAddressSerializer(many=True, required=False)

    class Meta:
        model = Customer
        exclude = ['id', 'is_superuser', 'is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions', 'role', 'otp']
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
        CustomerProfile.objects.create(user=instance,  **profile)
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



class BankAccountSerializer(ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = BankAccount
        fields = '__all__'

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        instance.account_num = validated_data.get('account_num', instance.account_num)
        instance.account_name = validated_data.get('account_name', instance.account_name)
        instance.bank_name = validated_data.get('bank_name', instance.bank_name)
        instance.save()
        return instance