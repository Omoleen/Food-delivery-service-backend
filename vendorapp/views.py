from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from .models import (MenuCategory,
                     MenuItem,
                     VendorTransactionHistory,
                     Order)
from users.models import (Vendor,
                          VendorProfile,)
from .serializers import (MenuCategorySerializer,
                          MenuItemSerializer,
                          MenuItemImageSerializer,
                          VendorTransactionHistorySerializer,
                          VendorOrderSerializer)
from users.serializers import (VendorSerializer,
                               VendorProfileSerializer)
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import IntegrityError
from customerapp.serializers import OrderSerializer
from drf_spectacular import openapi
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema


class CategoryList(generics.GenericAPIView):
    serializer_class = MenuCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        all_categories = MenuCategory.objects.filter(vendor=request.user)
        # return Response(all_categories.values(), status=status.HTTP_200_OK)
        return Response(self.serializer_class(all_categories, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetails(generics.GenericAPIView):
    serializer_class = MenuCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = MenuCategory.objects.all()

    # def get_object(self, pk):
    #     try:
    #         return MenuCategory.objects.get(pk=pk)
    #     except MenuCategory.DoesNotExist:
    #         return None

    def get(self, request, *args, **kwargs):
        category = self.get_object()
        if category is not None:
            if category.vendor == request.user:
                return Response(self.serializer_class(category).data, status=status.HTTP_200_OK)

        return Response({'error': 'PK is not existent'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        category = self.get_object()
        if category is not None:
            if category.vendor == request.user:
                category.name = request.data['name']
                category.save()
                return Response(self.serializer_class(category).data, status=status.HTTP_200_OK)
        return Response({'error': 'PK is not existent'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        if category is not None:
            if category.vendor == request.user:
                category.delete()
                return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'PK is not existent'}, status=status.HTTP_400_BAD_REQUEST)


class ItemList(generics.GenericAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        all_items = MenuItem.objects.filter(vendor=request.user)
        # return Response(all_items.values(), status=status.HTTP_200_OK)
        return Response(self.serializer_class(all_items, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError:
            return Response({'error': 'Item already exists'}, status=status.HTTP_400_BAD_REQUEST)


class MenuItemImage(generics.GenericAPIView):
    serializer_class = MenuItemImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = MenuItem.objects.all()
    parser_classes = (MultiPartParser, FormParser)

    def patch(self, request, *args, **kwargs):
        item = self.get_object()
        if item.vendor == request.user:
            serializer = self.serializer_class(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'pk does not exist'}, status=status.HTTP_204_NO_CONTENT)

    def get(self, request, *args, **kwargs):
        item = self.get_object()
        if item.vendor == request.user:
            serializer = self.serializer_class(item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'pk does not exist'}, status=status.HTTP_204_NO_CONTENT)


class ItemDetails(generics.GenericAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = MenuItem.objects.all()

    # def get_object(self, pk):
    #     try:
    #         return MenuItem.objects.get(pk=pk)
    #     except MenuItem.DoesNotExist:
    #         return None

    def get(self, request, *args, **kwargs):
        item = self.get_object()
        if item.vendor == request.user:
            return Response(self.serializer_class(item).data, status=status.HTTP_200_OK)
        return Response({'error': 'PK is not existent'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        item = self.get_object()
        if item.vendor == request.user:
            item.name = request.data.get('price', item.price)
            item.category_id = request.data.get('category_id', item.category_id)
            item.quantity = request.data.get('quantity', item.quantity)
            # item.image = request.data.get('image', item.image)  # handle file upload
            item.availability = request.data.get('availability', item.availability)
            item.save()
            return Response(self.serializer_class(item).data, status=status.HTTP_200_OK)
        return Response({'error': 'PK is not existent'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        if item.vendor == request.user:
            item.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'PK is not existent'}, status=status.HTTP_400_BAD_REQUEST)


class VendorDetails(generics.GenericAPIView):
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role == 'VENDOR':
            request.user.__class__ = Vendor
            serializer = self.serializer_class(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'This is not a Vendor'}, status=status.HTTP_400_BAD_REQUEST)


class VendorProfileView(generics.GenericAPIView):
    serializer_class = VendorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        if request.user.role == 'VENDOR':
            request.user.__class__ = Vendor
            serializer = self.serializer_class(request.user.profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'This is not a Vendor'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        if request.user.role == 'VENDOR':
            request.user.__class__ = Vendor
            serializer = self.serializer_class(request.user.profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'This is not a Vendor'}, status=status.HTTP_400_BAD_REQUEST)


class TransactionHistoryList(generics.GenericAPIView):
    serializer_class = VendorTransactionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        all_trxns = request.user.transactions.all()
        # return Response(all_items.values(), status=status.HTTP_200_OK)
        return Response(self.serializer_class(all_trxns, many=True).data, status=status.HTTP_200_OK)


class TransactionHistoryDetails(generics.GenericAPIView):
    serializer_class = VendorTransactionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = VendorTransactionHistory.objects.all()

    def get(self, request, *args, **kwargs):
        trxn = self.get_object()
        if trxn.vendor == request.user:
            return Response(self.serializer_class(trxn).data, status=status.HTTP_200_OK)
        return Response({'error': 'PK is not existent'}, status=status.HTTP_400_BAD_REQUEST)


class OrderList(generics.GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permissions_classes = [permissions.IsAuthenticated]

    def get(self, request):
        print('all')
        serializer = self.serializer_class(request.user.vendor_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderDetail(generics.GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = VendorOrderSerializer
    permissions_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    # id_param_config = openapi.OpenApiParameter(
    #     'id', location='path', description='order id', type=OpenApiTypes.STR)

    # @extend_schema(parameters=[id_param_config])
    def get(self, request, *args, **kwargs):
        order = self.get_object()
        if order is not None:
            if order.vendor == request.user:
                return Response(self.serializer_class(order).data, status=status.HTTP_200_OK)

        return Response({'error': 'order is not existent'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        if order is not None:
            if order.vendor == request.user:
                serializer = self.serializer_class(order, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'order does not existent'}, status=status.HTTP_400_BAD_REQUEST)