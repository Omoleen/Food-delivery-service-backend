import random

from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from .models import (RiderLoan,
                     RiderLoanPayment, RiderWalletHistory)
from customerapp.serializers import OrderSerializer
from vendorapp.models import Order
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


class RiderOrderSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=64, write_only=True)
    accept = serializers.BooleanField(write_only=True)
    order = OrderSerializer(read_only=True, allow_null=True)

    class Meta:
        exclude = []

    def create(self, validated_data):
        order = Order.objects.get(id=validated_data['id'])
        if validated_data['accept']:
            order.rider = self.context['request'].user
            order.status = Order.StatusType.ON_DELIVERY
            # TODO change order status after a rider's acceptance
            order.save()
        return order

    def validate(self, attrs):
        super().validate(attrs)
        try:
            order = Order.objects.get(id=attrs['id'])
            if order.rider is not None:
                raise serializers.ValidationError(
                    {
                        'id': 'Another Rider is in charge of this order'
                    }
                )
        except Order.DoesNotExist:
            raise serializers.ValidationError(
                {
                    'id': 'Order does not exist'
                }
            )
        return attrs

    def to_representation(self, instance):
        representation = {}
        representation['order'] = OrderSerializer(instance=instance).data
        return representation
