from decimal import Decimal

from rest_framework.serializers import (ModelSerializer,
                                        Serializer)
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber

from users.utils import generate_ref
from .models import (CustomerDeliveryAddress,
                     CustomerTransactionHistory)
from users.models import (CustomerOrder,
                          OrderSubItem,
                          VendorOrder,
                          MenuItem,
                          OrderItem,
                          MenuCategory,
                          MenuSubItem,
                          OrderItem,
                          MenuItem,
                          MenuSubItem,
                          MenuCategory, )
from users.models import (Customer,
                          Vendor,
                          VendorProfile)
from json import loads, dumps
from django.urls import reverse
import requests
from pprint import pprint
from django.conf import settings


class CustomerDeliveryAddressSerializer(ModelSerializer):
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CustomerDeliveryAddress
        fields = '__all__'
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        instance.number = validated_data.get('number', instance.number)
        instance.address = validated_data.get('address', instance.address)
        instance.landmark = validated_data.get('landmark', instance.landmark)
        instance.label = validated_data.get('label', instance.label)
        instance.save()
        return instance


class OrderSubItemSerializer(ModelSerializer):

    class Meta:
        model = OrderSubItem
        exclude = ['item']
        read_only_fields = ['id']



class OrderItemSerializer(ModelSerializer):
    item_id = serializers.IntegerField(write_only=True)
    sub_items = OrderSubItemSerializer(many=True)

    class Meta:
        model = OrderItem
        exclude = ['customer_order', 'vendor_order', 'item']
        read_only_fields = ['id', 'amount']

    def validate(self, attrs):
        super().validate(attrs)
        if not MenuItem.objects.filter(id=attrs['item_id']).exists():
            raise serializers.ValidationError({
                'sub_item': f'Item id - {attrs["item_id"]} does not exist'
            })
        return attrs


class CustomerOrderSerializer(ModelSerializer):
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    customer_order_items = OrderItemSerializer(many=True)
    customer_address_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = CustomerOrder
        # fields = ['id', 'customer', 'type', 'delivery_address', 'location', 'phone_number', 'payment_method', 'third_party_name', 'note', 'delivery_fee', 'vat', 'items']
        read_only_fields = ['id', 'location', 'vendor', 'rider', 'total_amount', 'created', 'updated', 'total_delivery_fee']
        exclude = []

    def create(self, validated_data):
        items = validated_data.pop('customer_order_items')
        customer_address_id = validated_data.pop('customer_address_id')
        address = self.context['request'].user.customer_addresses.get(id=customer_address_id)
        validated_data['delivery_address'] = f'{address.number}, {address.address}'
        validated_data['location'] = address.label
        vendor_orders = {}
        item_amounts = []

        validated_data['phone_number'] = validated_data.get('phone_number', self.context['request'].user.phone_number)
        delivery_fees = []  # TODO Delivery fee
        for item in items:
            serializer = OrderItemSerializer(data=item)
            if serializer.is_valid():
                menu_item = MenuItem.objects.get(id=item.get('item_id'))
                item_amounts.append(menu_item.price)
        validated_data['total_amount'] = Decimal(sum(item_amounts))
        if validated_data['payment_method'] == CustomerOrder.PaymentMethod.WALLET:
            if self.context['request'].user.wallet < validated_data['total_amount']:
                raise serializers.ValidationError({
                    'payment_method': 'you do not have enough money in your wallet to pay for this order'
                })
        elif validated_data['payment_method'] == CustomerOrder.PaymentMethod.WEB:
            pass
        # TODO handle delivery fee better
        order = self.Meta.model.objects.create(**validated_data)
        for item in items:
            sub_items = item.pop('sub_items')
            menu_item = MenuItem.objects.get(id=item.get('item_id'))
            item_amounts.append(menu_item.price)
            if vendor_orders.get(menu_item.vendor_id) is None:
                vendor_orders[menu_item.vendor_id] = VendorOrder.objects.create(order=order, vendor_id=menu_item.vendor_id, delivery_fee=Decimal(300), amount=menu_item.price)
            else:
                vendor_orders[menu_item.vendor_id].amount += menu_item.price
                vendor_orders[menu_item.vendor_id].save()
            item.pop('item_id')
            item_instance = OrderItem.objects.create(item=menu_item, amount=menu_item.price, customer_order=order, vendor_order=vendor_orders[menu_item.vendor_id], **item)
            sub_items_instances = []
            for sub_item in sub_items:
                if menu_item.sub_items.filter(name=sub_item['name']).exists():
                    sub = menu_item.sub_items.get(name=sub_item['name'])
                    if sub.max_num_choices < len(sub_item['choices']):
                        raise serializers.ValidationError({
                            'choices': f'A maximum of {sub.max_num_choices} choice is allowed for {sub_item["name"]}'
                        })
                    for req_choice in sub_item['choices']:
                        if not sub.choices.__contains__(req_choice):
                            raise serializers.ValidationError({
                                'choices': f'{req_choice} is not valid in {sub_item["name"]}'
                            })
                    sub_items_instances.append(OrderSubItem(item=item_instance, **sub_item))
                else:
                    raise serializers.ValidationError({
                        'sub_item': f'Sub item - {sub_item["name"]} does not exit'
                    })
            OrderSubItem.objects.bulk_create(sub_items_instances)
        if validated_data.get('type') == CustomerOrder.OrderType.DELIVERY:
            order.total_delivery_fee = validated_data['total_delivery_fee'] = Decimal(len(vendor_orders) * 300)
            order.total_amount += validated_data['total_delivery_fee']
        order.save()
        return order

    def validate(self, attrs):
        super().validate(attrs)
        if not self.context['request'].user.customer_addresses.filter(id=attrs['customer_address_id']).exists():
            raise serializers.ValidationError({'customer_address_id': "customer_address_id does not exist"})
        return attrs

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class CustomerTransactionHistorySerializer(ModelSerializer):

    class Meta:
        model = CustomerTransactionHistory
        exclude = ['customer']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation.get('transaction_id'):
            representation.pop('delivery_id')
            representation.pop('restaurant')
            if instance.transaction_status in [CustomerTransactionHistory.TransactionStatus.SUCCESS,
                                               CustomerTransactionHistory.TransactionStatus.FAILED]:
                representation.pop('checkout_url')
        elif representation.get('delivery_id'):
            representation.pop('transaction_id')
            representation.pop('transaction_status')
            representation.pop('checkout_url')
            representation.pop('payment_method')

        return representation


class CustomerMenuSubItemSerializer(ModelSerializer):

    class Meta:
        model = MenuSubItem
        read_only_fields = ['id']
        exclude = []


class CustomerMenuItemSerializer(ModelSerializer):
    sub_items = CustomerMenuSubItemSerializer(many=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'summary', 'price', 'quantity', 'image', 'sub_items']
        read_only_fields = ['id']


class CustomerMenuCategorySerializer(ModelSerializer):
    # vendor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    items = CustomerMenuItemSerializer(many=True)

    class Meta:
        model = MenuCategory
        fields = ['name', 'id', 'items']
        read_only_fields = ['id']


class VendorHomeProfileDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorProfile
        fields = ['business_name', 'preparation_time', 'minimum_order', 'average_star_rating', 'profile_picture']


class VendorHomeDetailSerializer(serializers.ModelSerializer):
    categories = CustomerMenuCategorySerializer(many=True)
    profile = VendorHomeProfileDetailSerializer()

    class Meta:
        model = Vendor
        fields = ['id', 'profile', 'categories']


class VendorHomeProfileListSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorProfile
        fields = ['business_name', 'preparation_time', 'minimum_order', 'average_star_rating', 'profile_picture']


class VendorHomeListSerializer(serializers.ModelSerializer):
    profile = VendorHomeProfileListSerializer()

    class Meta:
        model = Vendor
        fields = ['id', 'profile']


class MakeDepositSerializer(serializers.ModelSerializer):
    # amount = serializers.FloatField(write_only=True)
    title = serializers.CharField(max_length=264, default=CustomerTransactionHistory.TransactionTypes.WEB_TOP_UP, read_only=True)
    # transaction = CustomerTransactionHistorySerializer(read_only=True)

    class Meta:
        model = CustomerTransactionHistory
        exclude = ['delivery_id', 'restaurant', 'customer']
        read_only_fields = ['id', 'title', 'transaction_id', 'transaction_status', 'checkout_url', 'payment_method']

    def create(self, validated_data):
        deposit_transaction = CustomerTransactionHistory.objects.create(customer=self.context['user'],
                                                                        title=CustomerTransactionHistory.TransactionTypes.WEB_TOP_UP,
                                                                        transaction_id=generate_ref(),
                                                                        amount=self.validated_data['amount'])
        # checkout_url = 'test url'
        payload = {
            'amount': float(validated_data.get('amount')),
            'reference': deposit_transaction.transaction_id,
            'notification_url': settings.BASE_URL + reverse('users:korapay_webhooks'),
            'channels': ['bank_transfer', 'card', 'pay_with_bank'],
            'currency': 'NGN',
            'default_channel': 'card',
            'customer': {
                "email": self.context['user'].email,
            },
            'merchant_bears_cost': True
        }
        headers = {
            'Authorization': f'Bearer {settings.KORAPAY_SECRET_KEY}'
        }
        url = settings.KORAPAY_CHARGE_API
        response = requests.post(url=url, json=payload, headers=headers)

        if response.json()['status'] and 'success' in response.json()['message']:
            print(response.json())
            result = response.json()
            checkout_url = response.json()['data']['checkout_url']
            deposit_transaction.checkout_url = checkout_url
        else:
            deposit_transaction.transaction_status = CustomerTransactionHistory.TransactionStatus.FAILED
            deposit_transaction.payment_method = 'Failed'
        deposit_transaction.save()
        return deposit_transaction

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['amount'] <= 0:
            raise serializers.ValidationError({'amount': 'Amount should be greater than zero'})

        return attrs

