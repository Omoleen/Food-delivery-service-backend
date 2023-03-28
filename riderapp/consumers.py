from djangochannelsrestframework.decorators import action
from djangochannelsrestframework.consumers import AsyncAPIConsumer
from rest_framework import status
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin
from pprint import pprint
from djangochannelsrestframework.observer import model_observer
from users.models import Notification
from users.serializers import NotificationSerializer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
import json


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
