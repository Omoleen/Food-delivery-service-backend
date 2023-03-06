from users.models import (Rider, RiderProfile)
from users.serializers import (RiderSerializer, RiderProfileSerializer)
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser


class RiderDetails(generics.GenericAPIView):
    serializer_class = RiderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role == 'RIDER':
            request.user.__class__ = Rider
            serializer = self.serializer_class(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'This is not a Rider'}, status=status.HTTP_400_BAD_REQUEST)


class RiderProfileView(generics.GenericAPIView):
    serializer_class = RiderProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        if request.user.role == 'RIDER':
            request.user.__class__ = Rider
            serializer = self.serializer_class(request.user.profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'This is not a Rider'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """
            Only 'rider_available' and 'profile_picture' are mutable
        """
        if request.user.role == 'RIDER':
            request.user.__class__ = Rider
            serializer = self.serializer_class(request.user.profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'This is not a rider'}, status=status.HTTP_400_BAD_REQUEST)


# class LoadView(generics.GenericAPIView):
#     pass