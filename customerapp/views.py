from rest_framework import (generics,
                            status,
                            views,
                            permissions)
from rest_framework.response import Response
from users.models import (Customer,
                          CustomerProfile,
                          User,
                          Vendor,
                          VendorProfile,
                          CustomerTransactionHistory)
from pprint import pprint
from .serializers import (CustomerDeliveryAddressSerializer,
                          CustomerTransactionHistorySerializer,
                          CustomerOrderSerializer,
                          VendorHomeDetailSerializer,
                          VendorHomeListSerializer,
                          MakeDepositSerializer)
from .models import (CustomerDeliveryAddress,
                     )
# from users.models import (Order, OrderItem, MenuCategory, MenuItem, MenuSubItem)
from users.serializers import (CustomerSerializer,
                               CustomerProfileSerializer)
from rest_framework.parsers import (MultiPartParser,
                                    FormParser)
from django.db.models import Q
from drf_spectacular import openapi
from drf_spectacular.types import OpenApiTypes
from .permissions import IsCustomer
from drf_spectacular.utils import extend_schema
from django.db import IntegrityError


class DeliveryAddressList(generics.GenericAPIView):
    serializer_class = CustomerDeliveryAddressSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        return self.request.user.customer_addresses.all()

    def get(self, request):
        return Response(self.serializer_class(self.get_queryset(), many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeliveryAddressDetail(generics.GenericAPIView):
    serializer_class = CustomerDeliveryAddressSerializer
    permission_classes = [IsCustomer]

    def get_queryset(self):
        return self.request.user.customer_addresses.all()

    def get(self, request, *args, **kwargs):
        address = self.get_object()
        return Response(self.serializer_class(address).data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_object(), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        address = self.get_object()
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderList(generics.GenericAPIView):
    serializer_class = CustomerOrderSerializer
    permissions_classes = [IsCustomer]

    def get_queryset(self):
        return self.request.user.customer_orders.all()

    def get(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetail(generics.GenericAPIView):
    serializer_class = CustomerOrderSerializer
    permissions_classes = [IsCustomer]
    lookup_field = 'id'

    def get_queryset(self):
        return self.request.user.customer_orders.all()

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        return Response(self.serializer_class(order).data, status=status.HTTP_200_OK)

    # def patch(self, request, *args, **kwargs):
    #     order = self.get_object()
    #     serializer = self.serializer_class(order, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetails(generics.GenericAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsCustomer]

    def get_object(self):
        self.request.user.__class__ = Customer
        return self.request.user

    def get(self, request):
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerProfileView(generics.GenericAPIView):
    serializer_class = CustomerProfileSerializer
    permissions = [IsCustomer]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        self.request.user.__class__ = Customer
        return self.request.user.profile

    def get(self, request):
        print(self.get_object())
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = self.serializer_class(request.user.profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerTransactionHistoryList(generics.GenericAPIView):
    permission_classes = [IsCustomer]
    serializer_class = CustomerTransactionHistorySerializer

    def get_queryset(self):
        return self.request.user.customer_transactions.all()

    def get(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerTransactionHistoryDetail(generics.GenericAPIView):
    permission_classes = [IsCustomer]
    serializer_class = CustomerTransactionHistorySerializer
    lookup_field = 'id'

    def get_queryset(self):
        return self.request.user.customer_transactions.all()

    def get_object(self):
        try:
            return self.queryset.get(Q(transaction_id=self.lookup_field) | Q(delivery_id=self.lookup_field))
        except CustomerTransactionHistory.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        transaction = self.get_object()
        return Response(self.serializer_class(transaction).data, status=status.HTTP_200_OK)


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
    permission_classes = [IsCustomer]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)