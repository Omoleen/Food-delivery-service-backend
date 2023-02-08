from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from .models import (MenuCategory,
                     MenuItem)
from users.models import Vendor
from .serializers import (MenuCategorySerializer,
                          MenuItemSerializer)


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
        print(request.data)
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        if item is not None:
            if item.vandor == request.user:
                return Response(self.serializer_class(item).data, status=status.HTTP_200_OK)
        return Response({'error': 'PK is not existent'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        item = self.get_object()
        if item is not None:
            if item.vandor == request.user:
                item.name = request.data.get('price', item.price)
                item.category_id = request.data.get('category_id', item.category_id)
                item.quantity = request.data.get('quantity', item.quantity)
                item.image = request.data.get('image', item.image)  # handle file upload
                item.save()
                return Response(self.serializer_class(item).data, status=status.HTTP_200_OK)
        return Response({'error': 'PK does not exist'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        if item is not None:
            if item.vandor == request.user:
                item.delete()
                return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'PK does not exist'}, status=status.HTTP_400_BAD_REQUEST)

