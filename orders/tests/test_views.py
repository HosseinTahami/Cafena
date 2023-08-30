from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from ..views import ReorderView, OrdersHistoryView
from ..models import Table, Order, OrderItem
from accounts.models import Customer
from cafe.models import Product
import json
import urllib.parse
from model_bakery import baker
from accounts.models import Personnel
from django.contrib.sessions.middleware import SessionMiddleware


class CheckoutViewTest(TestCase):
    def test_get(self):
        session_data = {
            "orders_info": {
                "order1": [
                    {"key1": "value1"},
                    {"key2": "value2"},
                    [1234567890],
                ],
                "order2": [
                    {"key3": "value3"},
                    {"key4": "value4"},
                    [9876543210],
                ],
            }
        }

        self.client.session.update(session_data)
        url = reverse("orders:checkout")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/checkout.html")
        # expected_initial = {"phone_number": [9876543210]}
        # self.assertEqual(response.context["form"].initial, expected_initial)


class CartViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_cart_view(self):
        response = self.client.get(reverse("orders:cart"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/cart.html")


class OrderRejectTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.personnel = baker.make(Personnel)
        self.order = baker.make(Order, personnel=self.personnel, status="p")

    def test_order_rejection(self):
        self.client.force_login(self.personnel)
        url = reverse("orders:order_reject", kwargs={"pk": self.order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accounts:dashboard"))
        updated_order = Order.objects.get(pk=self.order.pk)
        self.assertEqual(updated_order.status, "r")
        self.assertEqual(updated_order.personnel, self.personnel)


class OrderAcceptTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.personnel = baker.make(Personnel)
        self.order = baker.make(Order, personnel=self.personnel, status="p")

    def test_order_rejection(self):
        self.client.force_login(self.personnel)
        url = reverse("orders:order_accept", kwargs={"pk": self.order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("accounts:dashboard"))
        updated_order = Order.objects.get(pk=self.order.pk)
        self.assertEqual(updated_order.status, "a")
        self.assertEqual(updated_order.personnel, self.personnel)


class OrdersHistoryViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()
        cls.user = baker.make(Personnel)
        cls.order1 = baker.make(Order, id=1)
        cls.order2 = baker.make(Order, id=2)

    def test_get_with_orders(self):
        session_data = {
            "orders_info": {
                "1": [
                    {"key1": "value1"},
                    {"key2": "value2"},
                    [1234567890],
                ],
                "2": [
                    {"key3": "value3"},
                    {"key4": "value4"},
                    [9876543210],
                ],
            }
        }
        session = self.client.session
        session.update(session_data)
        session.save()
        response = self.client.get(reverse("orders:orders_history"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/orders_history.html")
        self.assertEqual(len(response.context["orders"]), 2)

    def test_get_without_orders(self):
        response = self.client.get(reverse("orders:orders_history"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/orders_history.html")
        self.assertIsNone(response.context["orders"])


class AddOrderViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.table = baker.make(Table, table_number=1)
        # cls.product = baker.make(Product, name="Test Product", price=10.00)
        cls.customer = baker.make(Customer, phone_number="09121111111")
        cls.cart = json.dumps(
            {
                "1": {
                    "name": "Test Product",
                    "price": 10.00,
                    "quantity": 2,
                    "sub_total": 20.00,
                },
                "total_price": 20.00,
            }
        )

    def test_post(self):
        self.client.cookies["cart"] = self.cart
        response = self.client.post(
            reverse("orders:add_order"),
            data={
                "phone_number": self.customer.phone_number,
                "table_number": self.table.table_number,
            },
        )

        self.assertEqual(response.status_code, 302)
        session = self.client.session.get("orders_info")
        self.assertEqual(len(session), 1)

        order = Order.objects.first()
        order_item = OrderItem.objects.first()

        self.assertEqual(session[str(order.id)][0]["price"], 10.00)
        self.assertEqual(session[str(order.id)][0]["quantity"], 2)
        self.assertEqual(session[str(order.id)][0]["sub_total"], 20.00)
        self.assertEqual(session[str(order.id)][1], 20.00)
        self.assertEqual(session[str(order.id)][2], self.customer.phone_number)

class ReOrderViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.table = baker.make(Table, table_number=1)
        cls.product = baker.make(Product, name="Test Product", price=10.00)
        cls.customer = baker.make(Customer, phone_number="09121111111")
        cls.order = baker.make(Order, id=1, table=cls.table, customer=cls.customer)
        cls.orderitem = baker.make(
            OrderItem,
            id=1,
            order=cls.order,
            product=cls.product,
            quantity=2,
            price=10.00,
        )

    def test_get(self):
        session_data = {
            "orders_info": {
                "1": [
                    {"key1": "value1"},
                    {"key2": "value2"},
                    [1234567890],
                ],
                "2": [
                    {"key3": "value3"},
                    {"key4": "value4"},
                    [9876543210],
                ],
            }
        }
        session = self.client.session
        session.update(session_data)
        session.save()
        url = reverse("orders:reorder", args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/reorder.html")
        expected_initial = {"phone_number": [9876543210]}
        self.assertEqual(response.context["form"].initial, expected_initial)

    def test_post(self):
        url = reverse("orders:reorder", args=[self.order.id])
        response = self.client.post(
            url,
            data={
                "phone_number": self.customer.phone_number,
                "table_number": self.table.table_number,
            },
        )

        self.assertEqual(response.status_code, 302)
        session = self.client.session.get("orders_info")
        self.assertEqual(len(session), 1)

        order = Order.objects.last()
        order_item = OrderItem.objects.last()

        self.assertEqual(session[str(order.id)][0]["price"], 10.00)
        self.assertEqual(session[str(order.id)][0]["quantity"], 2)
        self.assertEqual(session[str(order.id)][0]["sub_total"], 20.00)
        self.assertEqual(session[str(order.id)][1], 20.00)
        self.assertEqual(session[str(order.id)][2], self.customer.phone_number)
