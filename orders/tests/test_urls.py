from django.test import TestCase
from django.urls import reverse, resolve
from orders.views import AddOrderView, CartView, OrderAccept, OrderReject, CheckoutView


class TestOrdersUrls(TestCase):
    def test_AddOrderView(self):
        url = reverse("orders:add_order")
        self.assertEqual(resolve(url).func.view_class, AddOrderView)

    def test_CartView(self):
        url = reverse("orders:cart")
        self.assertEqual(resolve(url).func.view_class, CartView)

    def test_OrderAccept(self):
        url = reverse("orders:order_accept", args=("5",))
        self.assertEqual(resolve(url).func.view_class, OrderAccept)

    def test_OrderReject(self):
        url = reverse("orders:order_reject", args=("5",))
        self.assertEqual(resolve(url).func.view_class, OrderReject)

    def test_CheckoutView(self):
        url = reverse("orders:checkout")
        self.assertEqual(resolve(url).func.view_class, CheckoutView)
