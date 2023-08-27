from django.test import TestCase
from accounts.models import Customer ,OTPCode
from django.contrib.auth.models import User


class TestCustomerModel(TestCase):
    def test_model_str(self):
        customer = Customer.objects.create(name='ahmad',phone_number='09121234567')
        self.assertEqual(str(customer), '09121234567')

class TestOTPCode(TestCase):
    def test_OTPCode_str(self):
        otpcode=OTPCode.objects.create(phone_number='09121234567',code='123',created= 'True')
        self.assertEqual(str(otpcode), '09121234567 | 123')