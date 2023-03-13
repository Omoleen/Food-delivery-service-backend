from users.models import (Rider, RiderProfile)
from users.serializers import (RiderSerializer,
                               RiderProfileSerializer)
from rest_framework import (generics, status, views, permissions)
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import (LoanSerializer,
                          LoanRepaymentSerializer,
                          WalletHistorySerializer,
                          WalletWithdrawalSerializer,
                          RiderOrderSerializer)
from customerapp.serializers import OrderSerializer
from .models import (RiderLoan,
                     RiderLoanPayment, RiderWalletHistory)
from datetime import date


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


class HomeScreen(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        pass


class LoanListView(generics.GenericAPIView):
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        request.user.__class__ = Rider
        serializer = self.serializer_class(request.user.loans.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoanDetailView(generics.GenericAPIView):
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = RiderLoan.objects.all()

    def get_object(self):
        return self.get_queryset().get(id=self.kwargs['id'])

    def get(self, request, *args, **kwargs):
        loan = self.get_object()
        serializer = self.serializer_class(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoanRepaymentView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LoanRepaymentSerializer
    queryset = RiderLoanPayment.objects.all()

    def get_object(self):
        return RiderLoan.objects.get(id=self.kwargs['id']).payments.all()

    def get(self, request, *args, **kwargs):
        loan_payments = self.get_object()
        serializer = self.serializer_class(loan_payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WalletHistoryView(generics.GenericAPIView):
    serializer_class = WalletHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        trnxs = request.user.rider_transactions.all().order_by('date_time')
        serializer = self.serializer_class(trnxs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RiderWithdrawal(generics.GenericAPIView):
    serializer_class = WalletWithdrawalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrdersHistoryList(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = self.serializer_class(request.user.rider_orders.all().order_by('created'), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderAcceptDeclineView(generics.GenericAPIView):
    serializer_class = RiderOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
