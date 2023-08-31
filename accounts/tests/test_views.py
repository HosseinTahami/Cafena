from django.test import TestCase, Client, RequestFactory
from django.shortcuts import reverse
from ..forms import UserCustomerLoginForm, OTPForm
from ..views import UserVerifyView
from ..models import Personnel
from django.contrib.auth import get_user
from django.contrib.auth.models import AnonymousUser
from model_bakery import baker
from datetime import datetime
import pytz
from django.contrib.auth.models import Group
from orders.models import OrderItem, Order
from cafe.models import Product
from ..forms import OrderItemForm


class UserLoginViewTest(TestCase):
    def test_user_get_view(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/personnel_login.html")
        self.assertIsInstance(response.context["form"], UserCustomerLoginForm)

    def test_user_valid_post_view(self):
        form_data = {"phone_number": "09123456789"}
        response = self.client.post(reverse("accounts:login"), data=form_data)
        session = self.client.session["personnel_verify"]
        self.assertEqual(session["phone_number"], "09123456789")
        self.assertTrue(1000 <= session["code"] <= 9999)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:verify_personnel"))

    def test_user_not_valid_post_view(self):
        form_data = {"phone_number": "11111111111"}
        form = UserCustomerLoginForm(data=form_data)
        response = self.client.post(reverse("accounts:login"), data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/personnel_login.html")


class UserVerifyViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        group = Group.objects.create(name="manager")
        cls.personnel = baker.make(Personnel, phone_number="09123456789")
        group.user_set.add(cls.personnel)

    def test_valid_verify_post(self):
        session_data = {
            "personnel_verify": {
                "phone_number": "09123456789",
                "code": 1234,
                "created_at": datetime.now(tz=pytz.timezone("Asia/Tehran")).isoformat(),
            }
        }
        url = reverse("accounts:verify_personnel")
        session = self.client.session
        session.update(session_data)
        session.save()
        response = self.client.post(
            url, data={"digit1": "1", "digit2": "2", "digit3": "3", "digit4": "4"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:dashboard"))

    def test_invalid_verify_post(self):
        session_data = {
            "personnel_verify": {
                "phone_number": "09123456789",
                "code": 1234,
                "created_at": datetime.now(tz=pytz.timezone("Asia/Tehran")).isoformat(),
            }
        }
        url = reverse("accounts:verify_personnel")
        session = self.client.session
        session.update(session_data)
        session.save()
        response = self.client.post(
            url, data={"digit1": "1", "digit2": "2", "digit3": "3", "digit4": "5"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:verify_personnel"))


# class UserLogoutViewTestCase(TestCase):

#     def setUp(self):
#         self.personnel = baker.make(Personnel, phone_number="09111111111", password="12345678qQ")

#     def test_logout(self):
#         self.client.login(phone_number="09111111111", password="12345678qQ")
#         response = self.client.get(reverse('accounts:logout'))
#         self.assertEqual(response.status_code, 302)
#         user = get_user(self.client)
#         self.assertIsInstance(user, AnonymousUser)


class DashboardViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        group = Group.objects.create(name="manager")
        cls.personnel = baker.make(Personnel, phone_number="09123456789")
        group.user_set.add(cls.personnel)

    def test_get_dashboard_logged_in(self):
        self.client.force_login(self.personnel)
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/dashboard.html")

    def test_get_dashboard_not_logged_in(self):
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/accounts/dashboard/")


class SalesDashboardViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        group1 = Group.objects.create(name="manager")
        group2 = Group.objects.create(name="cashier")
        cls.personnel1 = baker.make(Personnel, phone_number="09123456789")
        cls.personnel2 = baker.make(Personnel, phone_number="09123456788")
        group1.user_set.add(cls.personnel1)
        group2.user_set.add(cls.personnel2)

    def test_get_sales_dashboard_logged_in_manager(self):
        self.client.force_login(self.personnel1)
        response = self.client.get(reverse("accounts:sales_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/sales_dashboard.html")

    def test_get_sales_dashboard_logged_in_not_manager(self):
        self.client.force_login(self.personnel2)
        response = self.client.get(reverse("accounts:sales_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_get_sales_dashboard_no_logged_in(self):
        response = self.client.get(reverse("accounts:sales_dashboard"))
        self.assertEqual(response.status_code, 302)


class OrdersDashboardViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        group1 = Group.objects.create(name="manager")
        group2 = Group.objects.create(name="cashier")
        cls.personnel1 = baker.make(Personnel, phone_number="09123456789")
        cls.personnel2 = baker.make(Personnel, phone_number="09123456788")
        group1.user_set.add(cls.personnel1)
        group2.user_set.add(cls.personnel2)

    def test_get_orders_dashboard_logged_in_manager(self):
        self.client.force_login(self.personnel1)
        response = self.client.get(reverse("accounts:orders_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/all_orders_table.html")

    def test_get_orders_dashboard_no_logged_in(self):
        response = self.client.get(reverse("accounts:orders_dashboard"))
        self.assertEqual(response.status_code, 302)


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        group1 = Group.objects.create(name="manager")
        group2 = Group.objects.create(name="cashier")
        cls.personnel1 = baker.make(Personnel, phone_number="09123456789")
        cls.personnel2 = baker.make(Personnel, phone_number="09123456788")
        group1.user_set.add(cls.personnel1)
        group2.user_set.add(cls.personnel2)
        cls.order1 = baker.make(Order, id=1)
        cls.product1 = baker.make(Product, id=1, _create_files=True)
        cls.orderitem1 = baker.make(
            OrderItem,
            id=1,
            product=cls.product1,
            order=cls.order1,
            quantity=50,
            price=10,
        )

    def test_get_orders_dashboard_logged_in_manager(self):
        self.client.force_login(self.personnel1)
        url = reverse("accounts:order_detail", args=[self.order1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/order_detail.html")

    def test_get_orders_dashboard_no_logged_in(self):
        url = reverse("accounts:order_detail", args=[self.order1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_post(self):
        data = {"quantity": 10, "product": self.orderitem1.product}
        self.client.force_login(self.personnel1)
        url = reverse("accounts:order_detail", kwargs={"pk": self.order1.id})
        response = self.client.post(url, data=data)
        form = OrderItemForm(data=data)
        self.assertTrue(form.is_valid())
        orderitem = OrderItem.objects.last()
        self.assertEqual(orderitem.quantity, 50)
