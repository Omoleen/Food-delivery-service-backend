from rest_framework import generics, status, views, permissions
from .serializers import (VerifyPhoneSerializer,
                          RegisterPhoneSerializer,
                          RiderSerializer,
                          VendorSerializer,
                          CustomerSerializer,
                          ReviewSerializer,
                          BankAccountSerializer,
                          PhoneGenerateOTPSerializer,
                          PhoneLoginSerializer,
                          NotificationSerializer)
from rest_framework.response import Response
from .models import (User,
                     Rider,
                     Customer,
                     Vendor,
                     VerifyPhone,
                     Review,
                     BankAccount,
                     Notification)
from rest_framework.parsers import MultiPartParser, FormParser


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
                    return Response(context, status=status.HTTP_200_OK)
                else:
                    context = {
                        'error': 'OTP invalid'
                    }
                    return Response(context, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(e)
                context = {
                    'error': 'Phone number is invalid'
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
            created = serializer.save()
            if created is None:
                return Response({'error': "There's an existing account on this phone number"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhoneNumberRequestOTPView(generics.GenericAPIView):
    serializer_class = PhoneGenerateOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                phone = VerifyPhone.objects.get(phone_number=request.data['phone_number'])
                print(phone.generate_code())
                phone.save()
                # send code to phone number
                return Response(serializer.data, status=status.HTTP_200_OK)
            except VerifyPhone.DoesNotExist:
                return Response({'error': 'phone number does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhoneNumberLoginOTPView(generics.GenericAPIView):
    serializer_class = PhoneLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                phone = VerifyPhone.objects.get(phone_number=request.data['phone_number'], otp=request.data['otp'])
                return Response(phone.get_tokens_for_user(), status=status.HTTP_200_OK)
            except VerifyPhone.DoesNotExist:
                return Response({'error': 'Incorrect OTP'}, status=status.HTTP_400_BAD_REQUEST)
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


class NotificationsListView(generics.GenericAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        all_notifs = request.user.notifications.all().order_by('date')
        return Response(self.serializer_class(all_notifs, many=True).data, status=status.HTTP_200_OK)


class BankAccountList(generics.GenericAPIView):
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        all_accounts = BankAccount.objects.filter(user=request.user)
        # return Response(all_reviews.values(), status=status.HTTP_200_OK)
        return Response(self.serializer_class(all_accounts, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BankAccountDetail(generics.GenericAPIView):
    serializer_class = BankAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = BankAccount.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            account = self.get_object()
            # if account is not None:
            if account.user == request.user:
                return Response(self.serializer_class(account).data, status=status.HTTP_200_OK)
        except BankAccount.DoesNotExist:
            return Response({'error': 'PK is not existent'}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        account = self.get_object()
        if account is not None:
            if account.user == request.user:
                serializer = self.serializer_class(account, data=request.data, partial=True)
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
        account = self.get_object()
        if account is not None:
            if account.user == request.user:
                account.delete()
                return Response({'status': 'success'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'PK is not existent'}, status=status.HTTP_400_BAD_REQUEST)