from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from .models import (CustomerDeliveryAddress,)
from vendorapp.models import (Order,
                              OrderItem, MenuItem, MenuSubItem)
from drf_yasg import openapi
from users.models import Customer


class CustomerDeliveryAddressSerializer(ModelSerializer):
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CustomerDeliveryAddress
        fields = '__all__'
        read_only_fields = ['id']


class OrderItemSerializer(ModelSerializer):
    # vendor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    item_id = serializers.IntegerField()
    # choice =

    class Meta:
        model = OrderItem
        # fields = '__all__'
        # read_only_fields = ['id']
        exclude = ['order', 'id', 'item']

    class CreateChoiceJSONField(serializers.JSONField):
        class Meta:
            swagger_schema_fields = {
                "type": openapi.TYPE_OBJECT,
                "properties": {
                    "sub_item_name": openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    # "id": openapi.Schema(
                    #     type=openapi.TYPE_STRING,
                    # ),
                },
                "required": [],

            }
    choice = CreateChoiceJSONField(allow_null=True)

    def validate(self, attrs):
        super().validate(attrs)
        choice = attrs.get('choice')
        item_id = attrs['item_id']
        try:
            item = MenuItem.objects.get(id=item_id)
        except MenuItem.DoesNotExist:
            raise serializers.ValidationError({"item_id": f"Item id - {item_id} does not exist"})
        if choice is not None:
            for key, value in choice.items():
                try:
                    sub_item = item.subitems.get(name=key)  # if there is an error then key does not exist
                except MenuSubItem.DoesNotExist:
                    raise serializers.ValidationError({"choice": f"There is no {key} section in {item.name}"})
                not_available = self.check_sub_item_list(value, sub_item.items)
                if len(not_available):
                    raise serializers.ValidationError({"choice": f"There is no {not_available} in {sub_item.name} section"})
                else:
                    if len(value) > sub_item.max_items:  # get the sub item with that name and compare the amount in each sub item to max items
                        raise serializers.ValidationError({"choice": f"a maximum of {sub_item.max_items} is allowed in the {key} section"})

        return attrs

    def check_sub_item_list(self, value, items_list):
        available = {}
        not_available = []
        for item in items_list:
            available[item['name']] = True
        for item in value:
            if not item in available:
                not_available.append(item)
        return not_available


class OrderSerializer(ModelSerializer):
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'type', 'delivery_address', 'location', 'phone_number', 'payment_method', 'third_party_name', 'note', 'delivery_fee', 'vat', 'items']
        read_only_fields = ['id']

    def create(self, validated_data):
        items = validated_data.pop('items')
        order = self.Meta.model.objects.create(**validated_data)
        all_items = [OrderItem(order_id=order.id, **item) for item in items]
        created_items = OrderItem.objects.bulk_create(all_items)
        order.vendor = created_items[0].item.vendor
        order.save()
        return order

    def validate(self, attrs):
        super().validate(attrs)
        if self.context['request'].user.role != 'CUSTOMER':
            raise serializers.ValidationError({'user': "user is not a customer"})
        return attrs