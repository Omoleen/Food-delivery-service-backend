from rest_framework.serializers import (ModelSerializer,
                                        Serializer)
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from .models import (CustomerDeliveryAddress,
                     CustomerTransactionHistory)
from vendorapp.models import (Order,
                              OrderItem,
                              MenuItem,
                              MenuSubItem,
                              MenuCategory)
from users.models import (Customer,
                          Vendor,
                          VendorProfile)


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


class OrderItemSerializer(ModelSerializer):
    item_id = serializers.IntegerField()
    choice = serializers.DictField(child=serializers.ListSerializer(child=serializers.CharField(max_length=100), allow_empty=True))

    class Meta:
        model = OrderItem
        exclude = ['order', 'id', 'item']

    def validate(self, attrs):
        super().validate(attrs)
        choice = attrs.get('choice')
        item_id = attrs['item_id']
        # print(attrs)
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
        # available = {}
        not_available = []
        # for item in items_list:
        #     available[item['name']] = True
        # for item in value:
        #     # temp = {}  # come back to this, convert the value to a dictionary with key name and check if it is in the item list directly
        #     if not item in available:
        #         not_available.append(item)
        for item in value:
            if {'name': item} not in items_list:
                not_available.append(item)
        return not_available


class OrderSerializer(ModelSerializer):
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    items = OrderItemSerializer(many=True, allow_null=True)
    customer_address_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = Order
        # fields = ['id', 'customer', 'type', 'delivery_address', 'location', 'phone_number', 'payment_method', 'third_party_name', 'note', 'delivery_fee', 'vat', 'items']
        read_only_fields = ['id', 'customer_address_id', 'location', 'vendor', 'rider', 'total', 'created', 'updated', 'vat', 'delivered_time', 'pickup_time', 'distance', 'delivery_fee', 'status']
        exclude = []

    def create(self, validated_data):
        items = validated_data.pop('items')
        customer_address_id = validated_data.get('customer_address_id')
        if customer_address_id is not None:
            validated_data.pop('customer_address_id')
            address = self.context['request'].user.customer_addresses.get(id=customer_address_id)
            validated_data['delivery_address'] = f'{address.number}, {address.address}'
            validated_data['location'] = address.label
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

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class CustomerTransactionHistorySerializer(ModelSerializer):

    class Meta:
        model = CustomerTransactionHistory
        exclude = ['customer', 'id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation.get('transaction_id'):
            representation.pop('delivery_id')
            representation.pop('restaurant')
        elif representation.get('delivery_id'):
            representation.pop('transaction_id')
            representation.pop('payment_method')

        return representation


# class VendorHomeSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         # model =
#         pass
#
#
# class VendorProfileSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = VendorProfile
#
#


class CustomerMenuSubItemSerializer(ModelSerializer):

    class Meta:
        model = MenuSubItem
        read_only_fields = ['id']
        fields = ['name', 'max_items', 'items', 'id']


class CustomerMenuItemSerializer(ModelSerializer):
    subitems = CustomerMenuSubItemSerializer(many=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'summary', 'price', 'quantity', 'image', 'subitems']
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
