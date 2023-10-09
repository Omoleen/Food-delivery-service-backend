from rest_framework import generics, status
from rest_framework.response import Response
from users.models import (MenuCategory,
                          MenuItem,
                          Vendor, User, VendorEmployee, VendorEmployeePair, CustomerOrder)
from .serializers import (MenuCategorySerializer,
                          MenuItemSerializer,
                          VendorTransactionHistorySerializer,
                          VendorOrderSerializer,
                          VendorMakeDepositSerializer, ManualOrderSerializer)
from users.serializers import (VendorSerializer,
                               VendorProfileSerializer,
                               VendorEmployeeSerializer,
                               VendorEmployeePairSerializer,
                               CreateVendorEmployeeSerializer)
from rest_framework.parsers import MultiPartParser, FormParser
from vendorapp.permissions import (IsVendor,
                                   IsVendorOrVendorEmployee)


class CategoryList(generics.GenericAPIView):
    serializer_class = MenuCategorySerializer
    permission_classes = [IsVendorOrVendorEmployee]

    def get_queryset(self):
        if self.request.user.role == User.Role.VENDOR:
            return self.request.user.categories.all()
        else:
            return self.request.user.vendor.vendor.categories.all()

    def get(self, request):
        return Response(self.serializer_class(self.get_queryset(), many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetails(generics.GenericAPIView):
    serializer_class = MenuCategorySerializer
    permission_classes = [IsVendorOrVendorEmployee]
    queryset = MenuCategory.objects.all()

    def get_queryset(self):
        if self.request.user.role == User.Role.VENDOR:
            return self.request.user.categories.all()
        else:
            return self.request.user.vendor.vendor.categories.all()

    def get(self, request, *args, **kwargs):
        category = self.get_object()
        return Response(self.serializer_class(category).data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        category = self.get_object()
        serializer = self.serializer_class(category, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ItemList(generics.GenericAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [IsVendorOrVendorEmployee]

    def get_queryset(self):
        if self.request.user.role == User.Role.VENDOR:
            return self.request.user.vendor_menu_items.all()
        else:
            return self.request.user.vendor.vendor.vendor_menu_items.all()

    def get(self, request):
        return Response(self.serializer_class(self.get_queryset(), many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemDetails(generics.GenericAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [IsVendorOrVendorEmployee]
    # parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        if self.request.user.role == User.Role.VENDOR:
            return self.request.user.vendor_menu_items.all()
        else:
            return self.request.user.vendor.vendor.vendor_menu_items.all()

    def get(self, request, *args, **kwargs):
        item = self.get_object()
        return Response(self.serializer_class(item).data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        item = self.get_object()
        serializer = self.serializer_class(item, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VendorDetails(generics.GenericAPIView):
    serializer_class = VendorSerializer
    permission_classes = [IsVendorOrVendorEmployee]

    def get_object(self):
        if self.request.user.role == User.Role.VENDOR:
            self.request.user.__class__ = Vendor
            return self.request.user
        else:
            return self.request.user.vendor.vendor

    def get(self, request):
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)


class VendorProfileView(generics.GenericAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [IsVendorOrVendorEmployee]
    # parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        if self.request.user.role == User.Role.VENDOR:
            self.request.user.__class__ = Vendor
            return self.request.user.profile
        else:
            return self.request.user.vendor.vendor.profile

    def get(self, request):
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = self.serializer_class(self.get_object(), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionHistoryList(generics.GenericAPIView):
    serializer_class = VendorTransactionHistorySerializer
    permission_classes = [IsVendorOrVendorEmployee]

    def get_queryset(self):
        if self.request.user.role == User.Role.VENDOR:
            return self.request.user.transactions.all()
        else:
            return self.request.user.vendor.vendor.transactions.all()

    def get(self, request):
        return Response(self.serializer_class(self.get_queryset(), many=True).data, status=status.HTTP_200_OK)


class TransactionHistoryDetails(generics.GenericAPIView):
    serializer_class = VendorTransactionHistorySerializer
    permission_classes = [IsVendorOrVendorEmployee]

    def get_queryset(self):
        if self.request.user.role == User.Role.VENDOR:
            return self.request.user.transactions.all()
        else:
            return self.request.user.vendor.vendor.transactions.all()

    def get(self, request, *args, **kwargs):
        trxn = self.get_object()
        return Response(self.serializer_class(trxn).data, status=status.HTTP_200_OK)


class OrderList(generics.GenericAPIView):
    serializer_class = VendorOrderSerializer
    permissions_classes = [IsVendorOrVendorEmployee]

    def get_queryset(self):
        if self.request.user.role == User.Role.VENDOR:
            return self.request.user.vendor_orders.filter(is_paid=True)
        else:
            return self.request.user.vendor.vendor.vendor_orders.filter(is_paid=True)

    def get(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderDetail(generics.GenericAPIView):
    serializer_class = VendorOrderSerializer
    permissions_classes = [IsVendorOrVendorEmployee]
    lookup_field = 'id'

    def get_queryset(self):
        if self.request.user.role == User.Role.VENDOR:
            return self.request.user.vendor_orders.filter(is_paid=True)
        else:
            return self.request.user.vendor.vendor.vendor_orders.filter(is_paid=True)

    def get_object(self):
        try:
            return self.get_queryset().get(order_id=self.kwargs['id'])
        except:
            return None

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        if order:
            return Response(self.serializer_class(order).data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        if order:
            serializer = self.serializer_class(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployeeList(generics.GenericAPIView):
    permission_classes = [IsVendor]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateVendorEmployeeSerializer
        else:
            return VendorEmployeePairSerializer

    def get_queryset(self):
        return VendorEmployeePair.objects.filter(vendor=self.request.user)

    def get(self, request):
        return Response(self.get_serializer_class()(self.get_queryset(), many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.get_serializer_class()(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_200_OK)


class EmployeeDetails(generics.GenericAPIView):
    permission_classes = [IsVendor]
    serializer_class = VendorEmployeeSerializer

    def get_queryset(self):
        return self.request.user.employee.all()

    def get_object(self):
        return self.get_queryset().get(employee_id=self.kwargs[self.lookup_field]).employee

    def get(self, request, *args, **kwargs):
        return Response(self.serializer_class(self.get_object()).data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_object(), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VendorMakeDepositView(generics.GenericAPIView):
    serializer_class = VendorMakeDepositSerializer
    permission_classes = [IsVendor]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManualOrderView(generics.GenericAPIView):
    permission_classes = [IsVendorOrVendorEmployee]
    serializer_class = ManualOrderSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)