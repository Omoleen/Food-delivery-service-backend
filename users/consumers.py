from django.contrib.gis.db.models.functions import Distance
from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from rest_framework import status
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin
from pprint import pprint
from djangochannelsrestframework.observer import model_observer
from users.models import Notification, Vendor, CustomerOrder, VendorOrder
from users.serializers import NotificationSerializer
from users.models import CustomerOrder, OrderItem
from customerapp.serializers import CustomerOrderSerializer, OrderItemSerializer
from vendorapp.serializers import VendorOrderSerializer

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import AccessToken

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
import json
from django.contrib.auth import get_user_model
User = get_user_model()


def authenticate_token(token):
    try:
        decoded_token = AccessToken(token)
        decoded_token.verify()
    # except TokenExpired:
    #     raise InvalidToken('Token has expired')
    except:
        raise InvalidToken('Token is invalid')
    else:
        user = JWTAuthentication().get_user(decoded_token)
        if user is not None:
            return user
        else:
            raise InvalidToken('User not found')

async_authenticate_token = sync_to_async(authenticate_token)


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
        if kwargs.get('accessToken'):
            try:
                user = await async_authenticate_token(kwargs.get('accessToken'))
                await self.notification_activity.subscribe(user=user, request_id=request_id)
                await self.send_json(NotificationSerializer(Notification.objects.filter(user=user), many=True).data)
            except InvalidToken:
                await self.send_json({"error": "Unauthorized"}, close=True)
        else:
            await self.send_json({'error': 'There is no access token'}, close=True)


class VendorRiderOrders(GenericAsyncAPIConsumer):

    @model_observer(VendorOrder)
    async def order_activity(
            self,
            message,
            observer=None,
            subscribing_request_ids=[],
            **kwargs
    ):
        await self.send_json(message)

    @order_activity.serializer
    def order_activity(self, instance: VendorOrder, action, **kwargs) -> dict:
        return {
            "action": action.value,
            "data": VendorOrderSerializer(instance).data
        }

    @order_activity.groups_for_signal
    def order_activity(self, instance: VendorOrder, **kwargs):
        if instance.vendor is not None:
            yield f'-vendor__{instance.vendor.id}__order'
        if instance.rider is not None:
            yield f'-rider__{instance.rider.id}__order'

    @order_activity.groups_for_consumer
    def order_activity(self, vendor=None, rider=None, **kwargs):
        if vendor is not None:
            yield f'-vendor__{vendor.id}__order'
        if rider is not None:
            yield f'-rider__{rider.id}__order'

    def filter_vendors(self, user):
        closest_vendors = Vendor.objects.annotate(distance=Distance('location', user.location)).filter(is_active=True,
                                                                                                       distance__lt=4000)
        # closest_vendors = None
        # TODO: location
        # pprint(closest_vendors.values())
        return closest_vendors

    @action()
    async def get_orders(self, request_id, **kwargs):
        global user
        if kwargs.get('accessToken'):
            try:
                user = await async_authenticate_token(kwargs.get('accessToken'))
            except InvalidToken:
                await self.send_json({"error": "Unauthorized"}, close=True)
        else:
            await self.send_json({'error': 'There is no access token'}, close=True)
        if user.role == User.Role.RIDER:
            closest_vendors = await database_sync_to_async(self.filter_vendors)(user)
            async for vendor in closest_vendors:
                await self.order_activity.subscribe(vendor=vendor, is_paid=True, status=VendorOrder.StatusType.READY, request_id=request_id)
            await self.order_activity.subscribe(rider=user, is_paid=True, request_id=request_id)
        elif user.role == User.Role.VENDOR:
            await self.order_activity.subscribe(vendor=user, is_paid=True, request_id=request_id)
        elif user.role == User.Role.VENDOR_EMPLOYEE:
            await self.order_activity.subscribe(vendor=user.vendor.vendor, is_paid=True, request_id=request_id)
