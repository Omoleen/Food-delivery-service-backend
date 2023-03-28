from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from rest_framework import status
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin
from pprint import pprint
from djangochannelsrestframework.observer import model_observer
from users.models import Notification
from users.serializers import NotificationSerializer
from vendorapp.models import Order, OrderItem
from customerapp.serializers import OrderSerializer, OrderItemSerializer

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
import json
from django.contrib.auth import get_user_model

User = get_user_model()


class MyConsumer(AsyncAPIConsumer):

    @action()
    async def an_async_action(self, some=None, **kwargs):
        if self.scope.get('user') is None:
            return {"Add the bearer token to the headers of your websockets connection"}, status.HTTP_401_UNAUTHORIZED
        user = self.scope.get('user')
        print(self.scope['user'])
        # do something async
        return {'response with': 'some message'}, status.HTTP_200_OK

    # @action()
    # def a_sync_action(self, pk=None, **kwargs):
    #     # do something sync
    #     return {'response with': 'some message'}, status.HTTP_200_OK


# This mixin consumer lets you subscribe to all changes of a specific instance,
# and also gives you access to the retrieve action.
# class UserConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

class Notifications(AsyncAPIConsumer):

    @model_observer(Notification)
    async def notification_activity(
            self,
            message,
            observer=None,
            subscribing_request_ids=[],
            **kwargs
    ):
        await self.send_json(message)

    @notification_activity.serializer
    def notification_activity(self, instance: Notification, action, **kwargs) -> dict:
        '''This will return the comment serializer'''
        # return NotificationSerializer(instance).data
        return {
            "action": action.value,
            "data": NotificationSerializer(instance).data
            }

    @notification_activity.groups_for_signal
    def notification_activity(self, instance: Notification, **kwargs):
        # yield f'-Ride__{instance.pk}'
        yield f'-Notif__{instance.user.id}'

    @notification_activity.groups_for_consumer
    def notification_activity(self, user=None, **kwargs):
        # if id is not None:
        yield f'-Notif__{user.id}'

    @action()
    async def get_notifications(self, request_id, **kwargs):
        if self.scope.get('user') is None:
            return {"Add the bearer token to the headers of your websockets connection"}, status.HTTP_401_UNAUTHORIZED
        user = self.scope.get('user')
        await self.notification_activity.subscribe(user=user, request_id=request_id)
        return [NotificationSerializer(each).data async for each in Notification.objects.filter(user=user)], \
               status.HTTP_200_OK


class Orders(GenericAsyncAPIConsumer):
    # serializer_class = OrderSerializer

    @model_observer(Order)
    async def order_activity(
            self,
            message,
            observer=None,
            subscribing_request_ids=[],
            **kwargs
    ):
        await self.send_json(message)

    @order_activity.serializer
    def order_activity(self, instance: Notification, action, **kwargs) -> dict:
        '''This will return the comment serializer'''
        # return NotificationSerializer(instance).data
        return {
            "action": action.value,
            "data": OrderSerializer(instance).data
            }

    @order_activity.groups_for_signal
    def order_activity(self, instance: Order, **kwargs):
        if instance.vendor is not None:
            yield f'-vendor__{instance.vendor.id}__order'
        yield f'-customer__{instance.customer.id}__order'
        if instance.rider is not None:
            yield f'-rider__{instance.rider.id}__order'

    @order_activity.groups_for_consumer
    def order_activity(self, vendor=None, customer=None, rider=None, **kwargs):
        if vendor is not None:
            yield f'-vendor__{vendor.id}__order'
        if customer is not None:
            yield f'-customer__{customer.id}__order'
        if rider is not None:
            yield f'-rider__{rider.id}__order'

    @action()
    async def get_orders(self, request_id, **kwargs):
        if self.scope.get('user') is None:
            return {"Add the bearer token to the headers of your websockets connection"}, status.HTTP_401_UNAUTHORIZED
        user = self.scope.get('user')
        if user.role == User.Role.RIDER:
            await self.order_activity.subscribe(rider=user, request_id=request_id)
            # return [await self.serializer_class(each).data async for each in Order.objects.filter(rider=user)], \
            #        status.HTTP_200_OK
        elif user.role == User.Role.CUSTOMER:
            await self.order_activity.subscribe(customer=user, request_id=request_id)
            # return [OrderSerializer(each).data async for each in Order.objects.filter(customer=user)], \
            #        status.HTTP_200_OK
        elif user.role == User.Role.VENDOR:
            await self.order_activity.subscribe(vendor=user, request_id=request_id)
            # return [await self.serializer_class(each).data async for each in Order.objects.filter(vendor=user)], \
            #        status.HTTP_200_OK
