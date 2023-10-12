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
                          RiderAcceptOrderSerializer,
                          RiderOrderSerializer)
from vendorapp.serializers import VendorOrderSerializer
from .models import (RiderLoan,
                     RiderLoanPayment,)
from datetime import date
from .permissions import IsRider


class RiderDetails(generics.GenericAPIView):
    serializer_class = RiderSerializer
    permission_classes = [IsRider]

    def get(self, request):
        request.user.__class__ = Rider
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RiderProfileView(generics.GenericAPIView):
    serializer_class = RiderProfileSerializer
    permission_classes = [IsRider]
    # parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        self.request.user.__class__ = Rider
        return self.request.user.profile

    def get(self, request):
        request.user.__class__ = Rider
        serializer = self.serializer_class(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """
            Only 'rider_available' and 'profile_picture' are mutable
        """
        request.user.__class__ = Rider
        serializer = self.serializer_class(self.get_object(), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HomeScreen(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        pass


class LoanListView(generics.GenericAPIView):
    serializer_class = LoanSerializer
    permission_classes = [IsRider]

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
    permission_classes = [IsRider]
    queryset = RiderLoan.objects.all()
    lookup_field = 'id'

    def get_queryset(self):
        return self.request.user.loans.all()

    def get(self, request, *args, **kwargs):
        loan = self.get_object()
        serializer = self.serializer_class(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoanRepaymentView(generics.GenericAPIView):
    permission_classes = [IsRider]
    serializer_class = LoanRepaymentSerializer
    queryset = RiderLoanPayment.objects.all()

    def get_queryset(self):
        return self.request.user.loans.filter()

    def get_object(self):
        return self.get_queryset().get(id=self.kwargs['id']).payments.all()

    def get(self, request, *args, **kwargs):
        loan_payments = self.get_object()
        serializer = self.serializer_class(loan_payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WalletHistoryView(generics.GenericAPIView):
    serializer_class = WalletHistorySerializer
    permission_classes = [IsRider]

    def get_queryset(self):
        return self.request.user.transactions.filter().order_by('date_time')

    def get(self, request):
        trnxs = self.get_queryset()
        serializer = self.serializer_class(trnxs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RiderWithdrawal(generics.GenericAPIView):
    serializer_class = WalletWithdrawalSerializer
    permission_classes = [IsRider]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrdersHistoryList(generics.GenericAPIView):
    serializer_class = RiderOrderSerializer
    permission_classes = [IsRider]

    def get_queryset(self):
        return self.request.user.rider_orders.filter().order_by('-id')

    def get(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderAcceptView(generics.GenericAPIView):
    serializer_class = RiderAcceptOrderSerializer
    permission_classes = [IsRider]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RiderOrderView(generics.GenericAPIView):
    serializer_class = RiderOrderSerializer
    permission_classes = [IsRider]
    lookup_field = 'id'

    def get_queryset(self):
        return self.request.user.rider_orders.filter(is_paid=True)

    def get_object(self):
        try:
            return self.get_queryset().get(order_id=self.kwargs['id'])
        except:
            return None

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        if order:
            return Response(self.serializer_class(order).data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        if order:
            serializer = self.serializer_class(order, data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RiderOrderList(generics.GenericAPIView):
    serializer_class = RiderOrderSerializer
    permission_classes = [IsRider]

    def get_queryset(self):
        return self.request.user.rider_orders.filter(is_paid=True)

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        print(self.get_queryset())
        return Response(serializer.data, status=status.HTTP_200_OK)
