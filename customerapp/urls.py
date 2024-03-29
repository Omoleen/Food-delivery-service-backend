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
from .views import (DeliveryAddressList,
                    DeliveryAddressDetail,
                    OrderList,
                    OrderDetail,
                    CustomerDetails,
                    CustomerProfileView,
                    CustomerTransactionHistoryDetail,
                    CustomerTransactionHistoryList,
                    HomeScreenVendorList,
                    HomeScreenVendorDetail,
                    MakeDepositView)
app_name = 'customerapp'
urlpatterns = [
    path('address/', DeliveryAddressList.as_view(), name='customer'),
    path('address/<int:pk>/', DeliveryAddressDetail.as_view()),
    path('orders/', OrderList.as_view()),
    path('orders/<str:id>/', OrderDetail.as_view()),
    path('details/', CustomerDetails.as_view()),
    path('profile/', CustomerProfileView.as_view()),
    path('transactions/', CustomerTransactionHistoryList.as_view()),
    path('transactions/<str:id>/', CustomerTransactionHistoryDetail.as_view()),
    path('home/', HomeScreenVendorList.as_view()),
    path('home/<int:pk>/', HomeScreenVendorDetail.as_view()),
    path('deposit/', MakeDepositView.as_view())


]
