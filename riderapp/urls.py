"""EatUp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import (RiderDetails,
                    RiderProfileView,
                    LoanListView,
                    LoanDetailView,
                    LoanRepaymentView,
                    WalletHistoryView,
                    RiderWithdrawal,
                    OrdersHistoryList,
                    OrderAcceptView,
                    RiderOrderView,
                    RiderOrderList)

app_name = 'riderapp'

urlpatterns = [
    path('details/', RiderDetails.as_view()),
    path('profile/', RiderProfileView.as_view()),
    path('loan/', LoanListView.as_view()),
    path('loan/<str:id>/', LoanDetailView.as_view()),
    path('loan/<str:id>/payments/', LoanRepaymentView.as_view()),
    path('wallet-history/', WalletHistoryView.as_view()),
    path('withdrawal/', RiderWithdrawal.as_view()),
    path('order-history/', OrdersHistoryList.as_view()),
    path('order/accept/', OrderAcceptView.as_view()),
    path('order/', RiderOrderList.as_view()),
    path('order/<str:id>/', RiderOrderView.as_view())
]
