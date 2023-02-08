from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from .models import (MenuCategory, MenuItem, MenuSubItem)


class MenuCategorySerializer(ModelSerializer):
    vendor = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = MenuCategory
        fields = ['vendor', 'name', 'id']
        read_only_fields = ['id']


class MenuSubItemSerializer(ModelSerializer):
    # vendor = serializers.HiddenField(default=serializers.CurrentUserDefault())

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
        fields = ['id', 'vendor', 'name', 'summary', 'price', 'quantity', 'image', 'category_id', 'subitems']
        read_only_fields = ['id', 'vendor']

    def create(self, validated_data):
        category_id = validated_data.pop('category_id')
        sub_items = validated_data.pop('subitems')
        instance = self.Meta.model.objects.create(category_id=category_id, **validated_data)
        all = [MenuSubItem(item=instance, **sub_item) for sub_item in sub_items]
        MenuSubItem.objects.bulk_create(all)
        return instance


