from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from users.models import VerifyPhone
import users.serializers as users_serializers


class VendorTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.data = {
            "phone_number": "+2349035467589"
        }
        self.url = reverse('users:register-phone')

    def test_vendor_registration(self):
        # Make a POST request to the view
        response = self.client.post(self.url, self.data, format='json')
        # Assert that the response status code is 201 Created
        assert response.status_code == status.HTTP_201_CREATED
        otp = VerifyPhone.objects.filter().first().otp
        self.data.update({'otp': otp})
        self.url = reverse('users:verify-phone')
        response = self.client.post(self.url, self.data, format='json')
        # Assert that the response status code is 201 Created
        assert response.status_code == status.HTTP_200_OK
        self.url = reverse('users:vendor-register')
        self.data = {
            "profile": {
                "user_rank": "Administrator"
            },
            "password": "qwerty123@",
            "first_name": "qw",
            "last_name": "fs",
            "email": "vend@wsdrjds.com",
            "phone_number": self.data['phone_number'],
            "city": "lagos"
        }
        response = self.client.post(self.url, self.data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def create_category(self):
        pass

