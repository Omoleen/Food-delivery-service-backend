from rest_framework.serializers import ModelSerializer, Serializer
from .models import (VerifyPhone,
                     RiderProfile,
                     Rider,
                     Vendor,
                     VendorProfile,
                     Customer,
                     CustomerProfile,
                     Review)
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber


class RegisterPhoneSerializer(ModelSerializer):

    class Meta:
        model = VerifyPhone
        fields = ['phone_number']
        extra_kwargs = {
            'phone_number': {'write_only': True}
        }


class VerifyPhoneSerializer(Serializer):
    phone_number = PhoneNumberField(region="NG")
    otp = serializers.IntegerField()

    class Meta:
        fields = ['phone_number', 'otp']
        extra_kwargs = {
            'phone_number': {'write_only': True},
            'otp': {'write_only': True}
        }


class RiderProfileSerializer(ModelSerializer):

    class Meta:
        model = RiderProfile
        exclude = ['user', 'id']
        read_only_fields = ['staff_id', 'orders_completed', 'rating', 'rider_available']


class RiderSerializer(ModelSerializer):
    profile = RiderProfileSerializer()

    class Meta:
        model = Rider
        exclude = ['id', 'is_superuser', 'is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions', 'role']
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
        read_only_fields = ['staff_id', 'orders_completed', 'rating', 'rider_available']


class VendorSerializer(ModelSerializer):
    profile = VendorProfileSerializer()

    class Meta:
        model = Vendor
        exclude = ['id', 'is_superuser', 'is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions', 'role']
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


class CustomerSerializer(ModelSerializer):
    profile = CustomerProfileSerializer()

    class Meta:
        model = Customer
        exclude = ['id', 'is_superuser', 'is_active', 'is_staff', 'is_admin', 'groups', 'user_permissions', 'role']
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
