from rest_framework import generics, status, views, permissions
from .serializers import (VerifyPhoneSerializer,
                          RegisterPhoneSerializer,
                          RiderSerializer,
                          VendorSerializer,
                          CustomerSerializer,
                          ReviewSerializer)
from rest_framework.response import Response
from .models import (User,
                     Rider,
                     Customer,
                     Vendor,
                     VerifyPhone,
                     Review)


class RegisterPhoneView(generics.GenericAPIView):

    serializer_class = RegisterPhoneSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                context = {
                    'phone_number': request.data['phone_number'],
                    'status': 'Verification Email/SMS successfully sent'
                }
                return Response(context, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            # create a background worker to delete phone numbers that have not been verified after an hour
            return Response({"error": "phone number already exists"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyPhoneView(generics.GenericAPIView):

    serializer_class = VerifyPhoneSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                phone = VerifyPhone.objects.get(phone_number=serializer.validated_data['phone_number'])
                if phone.otp == serializer.validated_data['otp']:
                    phone.is_verified = True
                    phone.save()
                    context = {
                        'phone_number': request.data['phone_number'],
                        'status': 'phone number verified'
                    }
                    return Response(context, status=status.HTTP_201_CREATED)
                else:
                    context = {
                        'error': 'OTP invalid'
                    }
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(e)
                context = {
                    'error': 'Phone number invalid'
                }
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RiderRegistrationView(generics.GenericAPIView):

    serializer_class = RiderSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            created = serializer.save()
            if created is None:
                return Response({'error': "There's an existing account on this phone number"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorRegistrationView(generics.GenericAPIView):

    serializer_class = VendorSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            created = serializer.save()
            if created is None:
                return Response({'error': "There's an existing account on this phone number"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerRegistrationView(generics.GenericAPIView):

    serializer_class = CustomerSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print(serializer.validated_data)
            created = serializer.save()
            if created is None:
                return Response({'error': "There's an existing account on this phone number"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewListView(generics.GenericAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        all_reviews = Review.objects.filter(reviewer=request.user)
        # return Response(all_reviews.values(), status=status.HTTP_200_OK)
        return Response(self.serializer_class(all_reviews, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    pass
