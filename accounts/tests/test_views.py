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


class ViewsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
    
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        # self.product = Product.objects.create(
        #     name="Test Product",
        #     category=self.category,
        #     price=10.0,
        # )
        self.product = baker.make(Product, category=self.category, _create_files=True)

        self.client = Client()
    
    def test_home_view(self):
        url = reverse("cafe:home")
        response = self.client.get(url)
    
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cafe/home.html")
        self.assertEqual(len(response.context["all_categories"]), 1)
        self.assertEqual(len(response.context["all_products"]), 1)
        self.assertIsInstance(response.context["form"], CartAddForm)
        self.assertIsInstance(response.context["page_data"], PageData)
    
    def test_product_detail_view(self):
        url = reverse("cafe:product_detail", kwargs={"pk": self.product.pk})
        response = self.client.get(url, pk=self.product.pk)
        # response = ProductDetailView.as_view()(request, pk=self.product.pk)
    
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cafe/product_detail.html")
    
        self.assertIn("product", response.context)
        self.assertIsInstance(response.context["product"], Product)
        self.assertIsInstance(response.context["form"], CartAddForm)
    
    def tearDown(self):
        self.product.delete()
        self.category.delete()
