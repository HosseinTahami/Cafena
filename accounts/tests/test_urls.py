from django.test import TestCase
from django.urls import reverse ,resolve
from accounts.views import UserLoginView ,UserLogoutView ,UserVerifyView ,ManageOrders


class TestaccountsUrls(TestCase):
    def test_UserLoginView(self):
        url=reverse('accounts:login')

        self.assertEqual(resolve(url).func.view_class,UserLoginView)

    def test_UserLogoutView(self):
        url=reverse('accounts:logout')

        self.assertEqual(resolve(url).func.view_class,UserLogoutView)
     

    def test_UserVerifyView(self):
        url=reverse('accounts:verify_personnel')

        self.assertEqual(resolve(url).func.view_class,UserVerifyView)


    def test_ManageOrders(self):
        url=reverse('accounts:manage_orders')

        self.assertEqual(resolve(url).func.view_class,ManageOrders)