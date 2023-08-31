from django.test import TestCase
from accounts.models import Customer 
from django.contrib.auth.models import User


class TestCustomerModel(TestCase):
    def test_model_str(self):
        customer = Customer.objects.create(name='ahmad',phone_number='09121234567')
        self.assertEqual(str(customer), '09121234567')

