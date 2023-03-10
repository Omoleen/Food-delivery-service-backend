from rest_framework.serializers import (ModelSerializer,
                                        Serializer)
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from .models import (MenuCategory,
                     MenuItem,
                     MenuSubItem,
                     OrderItem,
                     Order)


class MenuCategorySerializer(ModelSerializer):
    vendor = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = MenuCategory
        fields = ['vendor', 'name', 'id']
        read_only_fields = ['id']


class CreateSubItemJSONField(serializers.Serializer):
    name = serializers.CharField()

    class Meta:
        fields = ['name']


class MenuSubItemSerializer(ModelSerializer):

    items = serializers.ListSerializer(
        child=CreateSubItemJSONField(),
        allow_empty=True
    )

    class Meta:
        model = MenuSubItem
        read_only_fields = ['id']
        exclude = ['item']


class MenuItemSerializer(ModelSerializer):
    vendor = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category_id = serializers.IntegerField()
    subitems = MenuSubItemSerializer(many=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'vendor', 'name', 'summary', 'price', 'quantity', 'category_id', 'subitems', 'availability']
        # exclude = []
        read_only_fields = ['id', 'vendor']

    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        sub_items = validated_data.pop('subitems')
        instance = self.Meta.model.objects.create(category_id=category_id, **validated_data)
        all = [MenuSubItem(item=instance, **sub_item) for sub_item in sub_items]
        MenuSubItem.objects.bulk_create(all)
        return instance


class MenuItemImageSerializer(ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = MenuItem
        fields = ['image']

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
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
