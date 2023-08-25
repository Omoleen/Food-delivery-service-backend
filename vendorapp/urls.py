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
from .views import (CategoryList,
                    CategoryDetails,
                    ItemList,
                    ItemDetails,
                    VendorDetails,
                    VendorProfileView,
                    MenuItemImage,
                    TransactionHistoryDetails,
                    TransactionHistoryList,
                    OrderList,
                    OrderDetail, EmployeeList, EmployeeDetails)

app_name = 'vendorapp'

urlpatterns = [
    path('categories/', CategoryList.as_view()),
    path('categories/<int:pk>/', CategoryDetails.as_view()),
    path('items/', ItemList.as_view()),
    path('items/<int:pk>/', ItemDetails.as_view()),
    path('details/', VendorDetails.as_view()),
    path('profile/', VendorProfileView.as_view()),
    path('items/<int:pk>/image/', MenuItemImage.as_view()),
    path('trxns/', TransactionHistoryList.as_view()),
    path('trxns/<int:pk>/', TransactionHistoryDetails.as_view()),
    path('orders/', OrderList.as_view()),
    path('orders/<str:id>/', OrderDetail.as_view()),
    path('employees/', EmployeeList.as_view()),
    path('employees/<int:pk>/', EmployeeDetails.as_view())
]
