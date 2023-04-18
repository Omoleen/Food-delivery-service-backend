from rest_framework import (generics,
                            status,
                            views,
                            permissions)
from rest_framework.response import Response
from users.models import (Customer,
                          CustomerProfile,
                          User,
                          Vendor,
                          VendorProfile)
from pprint import pprint
from .serializers import (CustomerDeliveryAddressSerializer,
                          CustomerTransactionHistorySerializer,
                          OrderSerializer,
                          VendorHomeDetailSerializer,
                          VendorHomeListSerializer,
                          MakeDepositSerializer)
from .models import (CustomerDeliveryAddress,
                     CustomerTransactionHistory)
from users.models import (Order, OrderItem, MenuCategory, MenuItem, MenuSubItem)
from users.serializers import (CustomerSerializer,
                               CustomerProfileSerializer)
from rest_framework.parsers import (MultiPartParser,
                                    FormParser)
from django.db.models import Q
from drf_spectacular import openapi
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from django.db import IntegrityError


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
        # try:
        serializer = self.serializer_class(request.user.customer_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        # except Exception as e:
        #     print(e)
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """
        sub item name should be the key value in place of 'additionalProp'
        """
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()  # TODO we still require more code in the serializers, but creating an order works as at now
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetail(generics.GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permissions_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

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
    parser_classes = (MultiPartParser, FormParser)

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


class CustomerTransactionHistoryList(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerTransactionHistorySerializer

    def get(self, request):
        serializer = None
        try:
            serializer = self.serializer_class(request.user.customer_transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerTransactionHistoryDetail(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CustomerTransactionHistory.objects.all()
    serializer_class = CustomerTransactionHistorySerializer

    def get_object(self):
        try:
            return self.queryset.get(Q(transaction_id=self.id) | Q(delivery_id=self.id))
        except CustomerTransactionHistory.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        """
        pass in any id and you'll a record
        """
        self.id = kwargs.get('id')
        transaction = self.get_object()
        if transaction is not None:
            if transaction.customer == request.user:
                return Response(self.serializer_class(transaction).data, status=status.HTTP_200_OK)

        return Response({'error': 'transaction does not existent'}, status=status.HTTP_400_BAD_REQUEST)


class HomeScreenVendorList(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VendorHomeListSerializer
    project_param_config = openapi.OpenApiParameter(
        'popular', location='path', description='Description', type=OpenApiTypes.BOOL)
    id_param_config = openapi.OpenApiParameter(
        'under_30', location='path', description='Description', type=OpenApiTypes.BOOL)


    # @extend_schema(parameters=[project_param_config,
    #                            id_param_config])
    def get(self, request, *args, **kwargs):
        context = {}
        all_vendors = Vendor.objects
        # 'delivers to' should be taken into consideration when returning vendors
        context['popular'] = self.serializer_class(all_vendors.order_by('-vendorprofile__no_of_orders'), many=True).data
        # under 30 minutes
        context['under_30'] = self.serializer_class(all_vendors.filter(vendorprofile__preparation_time__lt=31), many=True).data
        # others
        context['others'] = self.serializer_class(all_vendors.all(), many=True).data
        return Response(context, status=status.HTTP_200_OK)


class HomeScreenVendorDetail(generics.GenericAPIView):
    queryset = Vendor.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VendorHomeDetailSerializer

    def get(self, request, *args, **kwargs):
        vendor = self.get_object()
        return Response(self.serializer_class(vendor).data, status=status.HTTP_200_OK)


class MakeDepositView(generics.GenericAPIView):
    serializer_class = MakeDepositSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if request.user.role == 'CUSTOMER':
            serializer = self.serializer_class(data=request.data, context={'user': request.user})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'only customers can deposit'}, status=status.HTTP_400_BAD_REQUEST)