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
from .views import (RegisterPhoneView,
                    VerifyPhoneView,
                    RiderRegistrationView,
                    VendorRegistrationView,
                    CustomerRegistrationView,
                    ReviewListView,
                    BankAccountList,
                    BankAccountDetail,
                    PhoneNumberRequestOTPView,
                    PhoneNumberLoginOTPView,
                    NotificationsListView,
                    KorapayWebHooksReceiver)

app_name = 'users'

urlpatterns = [
    path('register-phone/', RegisterPhoneView.as_view(), name='register-phone'),
    path('verify-phone/', VerifyPhoneView.as_view(), name='verify-phone'),
    path('rider/register/', RiderRegistrationView.as_view()),
    path('vendor/register/', VendorRegistrationView.as_view(), name='vendor-register'),
    path('customer/register/', CustomerRegistrationView.as_view()),
    path('reviews/', ReviewListView.as_view()),
    path('notifs/', NotificationsListView.as_view()),
    path('accounts/', BankAccountList.as_view()),
    path('accounts/<int:pk>/', BankAccountDetail.as_view()),
    path('phone/otp-request/', PhoneNumberRequestOTPView.as_view()),
    path('phone/otp-login/', PhoneNumberLoginOTPView.as_view()),
    path('webhooks/korapay/', KorapayWebHooksReceiver.as_view(), name='korapay_webhooks')
]
