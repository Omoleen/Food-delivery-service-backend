import requests
from rest_framework import generics, status, views, permissions
import json
from customerapp.models import CustomerTransactionHistory
from .serializers import (VerifyPhoneSerializer,
                          RegisterPhoneSerializer,
                          RiderSerializer,
                          VendorSerializer,
                          CustomerSerializer,
                          ReviewSerializer,
                          BankAccountSerializer,
                          PhoneGenerateOTPSerializer,
                          PhoneLoginSerializer,
                          NotificationSerializer, ListAvailableBanksSerializer, VerifyAccountDetailsSerializer,
                          WithdrawalSerializer, UpdateLocationViewSerializer)
from decimal import Decimal
from rest_framework.response import Response
from .models import (User,
                     Rider,
                     Customer,
                     Vendor,
                     VerifyPhone,
                     Review,
                     BankAccount,
                     Notification,
                     WebhooksPaymentMessage, VendorRiderTransactionHistory)
import hashlib
import hmac
from django.conf import settings
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
            except VerifyPhone.DoesNotExist:
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
            user = serializer.save()
            if user is None:
                return Response({'error': "There's an existing account on this phone number"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(user.get_tokens(), status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorRegistrationView(generics.GenericAPIView):
    serializer_class = VendorSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user is None:
                return Response({'error': "There's an existing account on this phone number"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(user.get_tokens(), status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerRegistrationView(generics.GenericAPIView):
    serializer_class = CustomerSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user is None:
                return Response({'error': "There's an existing account on this phone number"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(user.get_tokens(), status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhoneNumberRequestOTPView(generics.GenericAPIView):
    serializer_class = PhoneGenerateOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                phone_number = VerifyPhone.objects.get(phone_number=serializer.validated_data['phone_number'])
                phone_number.send_code()
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
        """
        Account name should be in uppercase, you can easily pass the response of the account details verification endpoint to not encounter issues

        """
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

    def delete(self, request, *args, **kwargs):
        account = self.get_object()
        if account is not None:
            if account.user == request.user:
                account.delete()
                return Response({'status': 'success'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'PK is not existent'}, status=status.HTTP_400_BAD_REQUEST)


class KorapayWebHooksReceiver(generics.GenericAPIView):
    SECRET_KEY = settings.KORAPAY_SECRET_KEY

    def post(self, request, *args, **kwargs):
        x_korapay_signature = request.headers.get('X-Korapay-Signature')
        if x_korapay_signature:
            print(request.data)
            # TODO verify the signature later
            message = request.data['data']
            if request.data['event'].startswith('charge'):
                try:
                    transaction = CustomerTransactionHistory.objects.get(transaction_id=message.get('reference'))
                    if message.get('status') == 'success':
                        transaction.transaction_status = CustomerTransactionHistory.TransactionStatus.SUCCESS
                        transaction.customer.wallet += Decimal(message.get('amount'))
                    else:
                        transaction.transaction_status = CustomerTransactionHistory.TransactionStatus.FAILED
                    transaction.payment_method = message.get('payment_method').replace('_', ' ').title()
                    transaction.save()
                    WebhooksPaymentMessage.objects.create(message=message,
                                                          user=transaction.customer,
                                                          event=request.data.get('event'),
                                                          status=message.get('status'),
                                                          reference=message.get('reference'),
                                                          payment_method=message.get('payment_method'))
                except CustomerTransactionHistory.DoesNotExist:
                    WebhooksPaymentMessage.objects.create(message=message,
                                                          # user=transaction.,
                                                          event=request.data.get('event'),
                                                          status=message.get('status'),
                                                          reference=message.get('reference'),
                                                          payment_method=message.get('payment_method'))
                    return Response({'status': 'Failed'}, status=status.HTTP_400_BAD_REQUEST)
            elif request.data['event'].startswith('transfer'):
                try:
                    transaction = VendorRiderTransactionHistory.objects.get(transaction_id=message.get('reference'))
                    if message.get('status') == 'success':
                        transaction.transaction_status = VendorRiderTransactionHistory.TransactionStatus.SUCCESS
                    else:
                        transaction.transaction_status = VendorRiderTransactionHistory.TransactionStatus.FAILED
                        transaction.user.wallet += transaction.amount
                    transaction.user.save()
                    WebhooksPaymentMessage.objects.create(message=message,
                                                          user=transaction.user,
                                                          event=request.data.get('event'),
                                                          status=message.get('status'),
                                                          reference=message.get('reference'))
                except VendorRiderTransactionHistory.DoesNotExist:
                    WebhooksPaymentMessage.objects.create(message=message,
                                                          event=request.data.get('event'),
                                                          status=message.get('status'),
                                                          reference=message.get('reference'))
                    return Response({'status': 'Failed'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': 'received'}, status=status.HTTP_200_OK)
        else:
            # TODO log the message
            return Response({'status': 'Failed'}, status=status.HTTP_400_BAD_REQUEST)


class ListAvailableBanks(generics.GenericAPIView):
    serializer_class = ListAvailableBanksSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        url = 'https://api.korapay.com/merchant/api/v1/misc/banks'
        headers = {
            'Authorization': f'Bearer {settings.KORAPAY_PUBLIC_KEY}'
        }
        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            serializer = self.serializer_class(response.json()['data'], many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Service Unavailable'}, status=status.HTTP_400_BAD_REQUEST)


class VerifyAccountDetails(generics.GenericAPIView):
    serializer_class = VerifyAccountDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MakeWithdrawalView(generics.GenericAPIView):
    serializer_class = WithdrawalSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateLocationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateLocationViewSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)