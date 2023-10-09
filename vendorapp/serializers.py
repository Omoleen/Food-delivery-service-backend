from decimal import Decimal

import requests
from django.conf import settings
from django.urls import reverse
from rest_framework.serializers import (ModelSerializer,
                                        Serializer)
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from users.models import (MenuCategory,
                          MenuItem,
                          MenuSubItem,
                          OrderItem,
                          VendorOrder, OrderSubItem, CustomerOrder, User, VendorEmployee, CustomerTransactionHistory,
                          VendorRiderTransactionHistory, )
from users.utils import generate_ref
from .models import VendorTransactionHistory
# from customerapp.serializers import OrderItemSerializer, CustomerOrderSerializer


class MenuCategorySerializer(ModelSerializer):
    vendor = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = MenuCategory
        fields = ['vendor', 'name', 'id']
        read_only_fields = ['id']

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if self.context['request'].user.categories.filter(name=attrs['name']).exists():
            raise serializers.ValidationError({
                'name': 'name already exists'
            })
        return attrs

    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.save()
        return instance


class MenuSubItemSerializer(ModelSerializer):

    class Meta:
        model = MenuSubItem
        read_only_fields = ['id']
        exclude = ['item']


class MenuItemSerializer(ModelSerializer):
    vendor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category_id = serializers.IntegerField()
    sub_items = MenuSubItemSerializer(many=True)

    class Meta:
        model = MenuItem
        exclude = []
        read_only_fields = ['id', 'vendor', 'category']

    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        sub_items = validated_data.pop('sub_items')
        if self.context['request'].user.role == User.Role.VENDOR_EMPLOYEE:
            validated_data['vendor'] = self.context['request'].user.vendor.vendor
        instance = self.Meta.model.objects.create(category_id=category_id, **validated_data)
        all_sub_items = [MenuSubItem(item=instance, **sub_item) for sub_item in sub_items]
        MenuSubItem.objects.bulk_create(all_sub_items)
        return instance

    def validate(self, attrs):
        if self.context['request'].method == 'POST':
            try:
                if self.context['request'].user.role == User.Role.VENDOR_EMPLOYEE:
                    category = MenuCategory.objects.get(id=attrs['category_id'], vendor=self.context['request'].user.vendor.vendor)
                else:
                    category = MenuCategory.objects.get(id=attrs['category_id'], vendor=self.context['request'].user)
                if category.items.filter(name=attrs['name']).exists():
                    raise serializers.ValidationError({'item': 'item already exists'})
            except MenuCategory.DoesNotExist:
                raise serializers.ValidationError({'category_id': 'Category does not exist'})
        if self.context['request'].user.role == User.Role.VENDOR_EMPLOYEE:
            self.context['request'].user.__class__ = VendorEmployee
            if not self.context['request'].user.profile.food_availability and attrs.get('availability') is not None:
                raise serializers.ValidationError({
                    'permissions': "You don't have permission to change the availability of this item"
                })
            if not self.context['request'].user.profile.price_change and attrs.get('price'):
                raise serializers.ValidationError({
                    'permissions': "You don't have permission to change the price of this item"
                })
        return super().validate(attrs)

    def update(self, instance, validated_data):
        if validated_data.get('name') and instance.category.items.filter(name=validated_data['name']).exists():
            raise serializers.ValidationError({'item': 'item already exists'})
        instance.price = validated_data.get('price', instance.price)
        instance.category_id = validated_data.get('category_id', instance.category_id)
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.name = validated_data.get('name', instance.name)
        instance.availability = validated_data.get('availability', instance.availability)
        # if validated_data.get('image') is not None:
        #     instance.image.save(validated_data.get('image').name, validated_data.get('image').file, save=True)
        instance.save()
        return instance


# class OrderItemSerializer(ModelSerializer):
#     # vendor = serializers.HiddenField(default=serializers.CurrentUserDefault())
#
#     class Meta:
#         model = OrderItem
#         fields = '__all__'
#         read_only_fields = ['id']
#
#
# class OrderSerializer(ModelSerializer):
#     customer = serializers.HiddenField(default=serializers.CurrentUserDefault())
#
#     class Meta:
#         model = Order
#         fields = ['id', 'customer', 'type', 'delivery_address', 'location', 'phone_number', 'payment_method', 'third_party_name', 'note', 'delivery_fee', 'vat']
#         read_only_fields = ['id']

class VendorTransactionHistorySerializer(ModelSerializer):

    class Meta:
        model = VendorTransactionHistory
        exclude =[]


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


class CustomerOrderSerializer(ModelSerializer):
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CustomerOrder
        read_only_fields = ['id', 'location', 'vendor', 'rider', 'total_amount', 'created', 'updated', 'total_delivery_fee']
        exclude = []

StatusTypeChoices = (
        ('READY', 'Ready'),
        ('IN_PROGRESS', 'In Progress'),
        ('CANCELLED', 'Cancelled')
    )


class VendorOrderSerializer(ModelSerializer):
    vendor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    vendor_order_items = OrderItemSerializer(many=True, allow_null=True, read_only=True)
    order = CustomerOrderSerializer(read_only=True)
    status = serializers.ChoiceField(choices=StatusTypeChoices)

    class Meta:
        model = VendorOrder
        read_only_fields = ['id',
                            'vat',
                            'delivered_time',
                            'pickup_time',
                            'delivery_fee',
                            'rider',
                            'amount',
                            'is_paid']
        exclude = []

    def update(self, instance: VendorOrder, validated_data):
        if validated_data.get('status') == VendorOrder.StatusType.CANCELLED:
            if instance.is_paid:
                if instance.amount > instance.vendor.wallet:
                    raise serializers.ValidationError({
                        'wallet': "You don't have enough money in your wallet to refund this order"
                    })
                instance.vendor.wallet -= instance.amount
                instance.vendor.save()
                if instance.order.customer:
                    instance.order.customer.wallet += instance.amount + Decimal('300')
                    instance.order.customer.save()
                    instance.order.customer.notifications.create(
                        title=f'Update on your {instance.order}',
                        content=f"Your order to {instance.vendor.profile.business_name} was cancelled and {instance.amount} has been refunded to your wallet with your delivery fee"
                    )
                    instance.order.customer.customer_transactions.create(
                        order=instance.order,
                        title=CustomerTransactionHistory.TransactionTypes.REFUND,
                        amount=instance.amount + Decimal('300'),
                        restaurant=instance.vendor.profile.business_name,
                        payment_method='wallet',
                        transaction_status=CustomerTransactionHistory.TransactionStatus.SUCCESS
                    )
        else:
            if instance.order.customer:
                instance.order.customer.notifications.create(
                    title=f'Update on your {instance.order}',
                    content=f'Your order is {validated_data.get("status").lower().replace("_", " ")}'
                )
        instance.status = validated_data['status']
        instance.save()
        # TODO decide on the logic for accepting orders etc
        return instance


class VendorMakeDepositSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=264,
                                  default=VendorRiderTransactionHistory.TransactionTypes.WEB_TOP_UP,
                                  read_only=True)

    class Meta:
        model = VendorRiderTransactionHistory
        exclude = ['order', 'comment', 'user']
        read_only_fields = ['id', 'title', 'date_time', 'transaction_id', 'payment_method', 'transaction_status', 'deposit_url']

    def create(self, validated_data):
        deposit_transaction = VendorRiderTransactionHistory.objects.create(user=self.context['user'],
                                                                            title=VendorRiderTransactionHistory.TransactionTypes.WEB_TOP_UP,
                                                                            transaction_id=generate_ref(),
                                                                            amount=self.validated_data['amount'])
        # checkout_url = 'test url'
        payload = {
            'amount': float(validated_data.get('amount')),
            'reference': f'deposit_{deposit_transaction.transaction_id}',
            'notification_url': settings.BASE_URL + reverse('users:korapay_webhooks'),
            'currency': 'NGN',
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
        print(print(response.json()))
        if response.ok:
            if response.json()['status'] and 'success' in response.json()['message']:
                print(response.json())
                result = response.json()
                deposit_url = response.json()['data']['checkout_url']
                deposit_transaction.deposit_url = deposit_url
            else:
                deposit_transaction.transaction_status = VendorRiderTransactionHistory.TransactionStatus.FAILED
                # deposit_transaction.payment_method = 'Failed'
        else:
            deposit_transaction.transaction_status = VendorRiderTransactionHistory.TransactionStatus.FAILED

        deposit_transaction.save()
        return deposit_transaction

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['amount'] <= 0:
            raise serializers.ValidationError({'amount': 'Amount should be greater than zero'})

        return attrs


class CustomOrderAddressSerializer(Serializer):
    house_number = serializers.IntegerField()
    address = serializers.CharField()
    landmark = serializers.CharField()


class CustomOrderItemSerializer(ModelSerializer):
    item_id = serializers.IntegerField(write_only=True)
    sub_items = OrderSubItemSerializer(many=True, required=False)
    vendor_order = VendorOrderSerializer(read_only=True)

    class Meta:
        model = OrderItem
        exclude = ['customer_order', 'item']
        read_only_fields = ['id', 'amount', 'vendor_order', 'name']

    def validate(self, attrs):
        super().validate(attrs)
        if not MenuItem.objects.filter(id=attrs['item_id']).exists():
            raise serializers.ValidationError({
                'sub_item': f'Item id - {attrs["item_id"]} does not exist'
            })
        return attrs


class ManualOrderSerializer(serializers.ModelSerializer):
    address = CustomOrderAddressSerializer(write_only=True)
    customer_order_items = CustomOrderItemSerializer(many=True)
    delivery_fee = serializers.FloatField(write_only=True)
    type = serializers.CharField(default=CustomerOrder.OrderType.DELIVERY)
    payment_method = serializers.CharField(default=CustomerOrder.PaymentMethod.WALLET)
    is_paid = serializers.BooleanField(default=True)

    class Meta:
        model = CustomerOrder
        read_only_fields = ['id', 'location', 'vendor', 'rider', 'total_amount', 'created', 'updated',
                            'total_delivery_fee', 'delivery_address', 'type', 'is_paid']
        exclude = ['customer']
        extra_kwargs = {
            'phone_number': {
                'required': True
            },
            'third_party_name': {
                'required': True
            }
        }

    def validate(self, attrs):
        customer_order_items = attrs['customer_order_items']
        for item in customer_order_items:
            if MenuItem.objects.get(id=item['item_id']).vendor != self.context['request'].user:
                raise serializers.ValidationError({
                    'vendor': 'This item belongs to another vendor'
                })
        if self.context['request'].user.wallet < attrs['delivery_fee']:
            raise serializers.ValidationError({
                'vendor': 'Wallet balance cannot pay delivery fee'
            })
        return super().validate(attrs)

    def create(self, validated_data):
        items = validated_data.pop('customer_order_items')
        address = validated_data.pop('address')
        delivery_fee = validated_data.pop('delivery_fee')
        validated_data['delivery_address'] = f"{address['house_number']}, {address['address']}, {address['landmark']}"
        validated_data['location'] = ''
        # print(validated_data)
        vendor_orders = {}
        menu_items = {}
        item_amounts = []
        transaction = None

        validated_data['phone_number'] = validated_data.get('phone_number')
        validated_data['third_party_name'] = validated_data.get('third_party_name')

        for item in items:
            menu_items[item.get('item_id')] = MenuItem.objects.get(id=item.get('item_id'))
            item_amounts.append(menu_items[item.get('item_id')].price * item.get('quantity'))
            vendor_orders[menu_items[item.get('item_id')].vendor_id] = True

        validated_data['total_delivery_fee'] = Decimal(delivery_fee)
        validated_data['total_amount'] = Decimal(sum(item_amounts)) + validated_data['total_delivery_fee']

        vendor_orders = {}
        order = self.Meta.model.objects.create(**validated_data)
        for item in items:
            sub_items = None
            if item.get('sub_items'):
                sub_items = item.pop('sub_items')
            menu_item = MenuItem.objects.get(id=item.get('item_id'))
            item_amount = menu_item.price * item['quantity']
            if vendor_orders.get(menu_item.vendor_id) is None:
                vendor_orders[menu_item.vendor_id] = VendorOrder.objects.create(order=order,
                                                                                vendor_id=menu_item.vendor_id,
                                                                                delivery_fee=delivery_fee,
                                                                                amount=item_amount,
                                                                                status=VendorOrder.StatusType.IN_PROGRESS,
                                                                                is_paid=True)
            else:
                vendor_orders[menu_item.vendor_id].amount += item_amount
                vendor_orders[menu_item.vendor_id].save()
            item.pop('item_id')
            item_instance = OrderItem.objects.create(item=menu_item, amount=menu_item.price, customer_order=order,
                                                     vendor_order=vendor_orders[menu_item.vendor_id], **item)
            if sub_items:
                # sub_items = item.pop('sub_items')
                sub_items_instances = []
                for sub_item in sub_items:
                    if menu_item.sub_items.filter(name=sub_item['name']).exists():
                        sub = menu_item.sub_items.get(name=sub_item['name'])
                        if sub.max_num_choices < len(sub_item['choices']):
                            order.delete()
                            raise serializers.ValidationError({
                                'choices': f'A maximum of {sub.max_num_choices} choice is allowed for {sub_item["name"]}'
                            })
                        for req_choice in sub_item['choices']:
                            if not sub.choices.__contains__(req_choice):
                                order.delete()
                                raise serializers.ValidationError({
                                    'choices': f'{req_choice} is not valid in {sub_item["name"]}'
                                })
                        sub_items_instances.append(OrderSubItem(item=item_instance, **sub_item))
                    else:
                        order.delete()
                        raise serializers.ValidationError({
                            'sub_item': f'Sub item - {sub_item["name"]} does not exit'
                        })
                OrderSubItem.objects.bulk_create(sub_items_instances)
        return order

