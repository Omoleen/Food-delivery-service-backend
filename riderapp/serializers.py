import random

from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber

from customerapp.serializers import VendorHomeListSerializer
from vendorapp.serializers import CustomerOrderSerializer, OrderItemSerializer
from .models import (RiderLoan,
                     RiderLoanPayment, RiderWalletHistory)
# from vendorapp.serializers import VendorOrderSerializer
from users.models import CustomerOrder, VendorOrder, Rider, VendorProfile, Vendor
import string



class LoanRepaymentSerializer(ModelSerializer):

    class Meta:
        model = RiderLoanPayment
        exclude = ['rider', 'rider_loan']


class LoanSerializer(ModelSerializer):
    rider = serializers.HiddenField(default=serializers.CurrentUserDefault())
    next_repayment = LoanRepaymentSerializer(default=None)

    class Meta:
        model = RiderLoan
        fields = ['id', 'repayment_plan', 'purpose', 'request_date', 'loan_amount', 'rider', 'status', 'amount_paid', 'next_repayment']
        read_only_fields = ['request_date', 'id', 'status', 'amount_paid', 'next_repayment']

    def create(self, validated_data):
        # print()
        validated_data['id'] = 'EU' + ''.join(random.choices(string.ascii_letters, k=6))
        return RiderLoan.objects.create(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.status not in ['PENDING', 'DECLINE']:
            representation['next_repayment'] = LoanRepaymentSerializer(instance.next_repayment).data
        return representation


class WalletHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = RiderWalletHistory
        exclude = ['rider']


class WalletWithdrawalSerializer(Serializer):
    rider = serializers.HiddenField(default=serializers.CurrentUserDefault())
    amount = serializers.FloatField(write_only=True)
    comment = serializers.CharField(max_length=64, write_only=True)
    status = serializers.CharField(default='success', max_length=64, read_only=True)

    class Meta:
        exclude = []

    def create(self, validated_data):
        print('logic to withraw')
        #TODO logic to withraw


class VendorOrderProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorProfile
        fields = ['business_name', 'preparation_time', 'minimum_order', 'average_star_rating', 'profile_picture', 'business_address', 'business_phone_number']


class VendorUserOrderSerializer(serializers.ModelSerializer):
    profile = VendorOrderProfileSerializer()

    class Meta:
        model = Vendor
        fields = ['id', 'profile', 'location_lat', 'location_long']


class RiderAcceptOrderSerializer(ModelSerializer):
    id = serializers.CharField(max_length=64, write_only=True)
    vendor_order_items = OrderItemSerializer(many=True, allow_null=True, read_only=True)
    order = CustomerOrderSerializer(read_only=True)
    vendor = VendorUserOrderSerializer(read_only=True)

    class Meta:
        model = VendorOrder
        read_only_fields = ['id',
                            'vat',
                            'delivered_time',
                            'pickup_time',
                            'delivery_fee',
                            'rider',
                            'amount',
                            'status',
                            ]
        exclude = []

    def create(self, validated_data):
        order = VendorOrder.objects.get(id=validated_data['id'])
        order.rider = self.context['request'].user
        order.status = VendorOrder.StatusType.ON_DELIVERY
        # TODO change order status after a rider's acceptance
        order.save()
        self.context['request'].user.__class__ = Rider
        self.context['request'].user.profile.rider_in_delivery = True
        self.context['request'].user.profile.save()
        return order

    def validate(self, attrs):
        super().validate(attrs)
        try:
            order = VendorOrder.objects.get(id=attrs['id'])
            if order.rider is not None:
                raise serializers.ValidationError(
                    {
                        'id': 'Another Rider is in charge of this order'
                    }
                )
        except VendorOrder.DoesNotExist:
            raise serializers.ValidationError(
                {
                    'id': 'Order does not exist'
                }
            )
        return attrs


StatusTypeChoices = (
        ('ON_DELIVERY', 'On Delivery'),
        ('ACCEPT_DELIVERY', 'Accept Delivery'),
        ('DELIVERED', 'Delivered'),
        ('DELIVERY_FAILED', 'Delivery Failed')
    )


class RiderOrderSerializer(ModelSerializer):
    rider = serializers.HiddenField(default=serializers.CurrentUserDefault())
    vendor_order_items = OrderItemSerializer(many=True, allow_null=True, read_only=True)
    order = CustomerOrderSerializer(read_only=True)
    status = serializers.ChoiceField(choices=StatusTypeChoices, write_only=True)

    class Meta:
        model = VendorOrder
        read_only_fields = ['id',
                            'vat',
                            'delivered_time',
                            'pickup_time',
                            'delivery_fee',
                            'vendor',
                            'amount']
        exclude = []

    def update(self, instance, validated_data):
        instance.status = validated_data['status']
        instance.save()
        # TODO decide on the logic for accepting orders etc
        return instance
