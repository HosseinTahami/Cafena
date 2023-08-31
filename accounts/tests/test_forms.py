from django.test import TestCase
from accounts.forms import UserCustomerLoginForm
from django.contrib.auth.models import User


# class TestUserCustomerLoginForm(TestCase):
#     def test_valid_data(self):
#         form = UserCustomerLoginForm(data={'phone_number':'09121234567',})
#         self.assertTrue(form.is_valid())

#     def test_empty_data(self):
#         form = UserCustomerLoginForm(data={})
#         self.assertFalse(form.is_valid())
#         self.assertEqual(len(form.errors), 1)