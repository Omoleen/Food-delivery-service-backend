from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from users.models import Customer, CustomerProfile, User
from .serializers import CustomerDeliveryAddressSerializer
from .models import CustomerDeliveryAddress
from customerapp.serializers import (OrderItemSerializer,
                                   OrderSerializer)
from vendorapp.models import (Order,
                              OrderItem)
from users.serializers import CustomerSerializer, CustomerProfileSerializer


class DeliveryAddressList(generics.GenericAPIView):
    serializer_class = CustomerDeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        all_addresses = CustomerDeliveryAddress.objects.filter(customer=request.user)
        # return Response(all_categories.values(), status=status.HTTP_200_OK)
        return Response(self.serializer_class(all_addresses, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeliveryAddressDetail(generics.GenericAPIView):
    serializer_class = CustomerDeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomerDeliveryAddress.objects.all()

    def get(self, request, *args, **kwargs):
        address = self.get_object()
        if address is not None:
            if address.customer == request.user:
                return Response(self.serializer_class(address).data, status=status.HTTP_200_OK)

        return Response({'error': 'PK is not existent'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        address = self.get_object()
        if address is not None:
            if address.customer == request.user:
                serializer = self.serializer_class(address, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                # address.number = request.data.get('number', address.number)
                # address.address = request.data.get('address', address.address)
                # address.landmark = request.data.get('landmark', address.landmark)
                # address.label = request.data.get('label', address.label)
                # address.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'PK is not existent'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        address = self.get_object()
        if address is not None:
            if address.customer == request.user:
                address.delete()
                return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'PK is not existent'}, status=status.HTTP_400_BAD_REQUEST)


class OrderList(generics.GenericAPIView):  # create orders and list all your orders
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permissions_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = None
        try:
            serializer = self.serializer_class(request.user.customer_orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()  # we still require more code in the serializers, but creating an order works as at now
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetail(generics.GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permissions_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        if order is not None:
            if order.customer == request.user:
                return Response(self.serializer_class(order).data, status=status.HTTP_200_OK)

        return Response({'error': 'order is not existent'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        if order is not None:
            if order.customer == request.user:
                serializer = self.serializer_class(order, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()

                    # order.number = request.data.get('number', order.number)
                    # order.address = request.data.get('address', order.address)
                    # order.landmark = request.data.get('landmark', order.landmark)
                    # order.label = request.data.get('label', order.label)
                    # order.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'order does not existent'}, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetails(generics.GenericAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role == 'CUSTOMER':
            request.user.__class__ = Customer
            serializer = self.serializer_class(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'This is not a customer'}, status=status.HTTP_400_BAD_REQUEST)


class CustomerProfileView(generics.GenericAPIView):
    serializer_class = CustomerProfileSerializer
    permissions = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role == 'CUSTOMER':
            request.user.__class__ = Customer
            serializer = self.serializer_class(request.user.profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'This is not a customer'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        if request.user.role == 'CUSTOMER':
            request.user.__class__ = Customer
            serializer = self.serializer_class(request.user.profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'This is not a customer'}, status=status.HTTP_400_BAD_REQUEST)
