from django.test import TestCase, RequestFactory
from django.urls import reverse
from cafe.models import Category, Product
from orders.forms import CartAddForm
from dynamic.models import PageData
from cafe.views import HomeView, ProductDetailView
from model_bakery import baker
from ..models import Contact
from model_bakery import baker


class HomeViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product1 = baker.make(Product, name="pizza", _create_files=True, category=self.category)
        self.product2 = baker.make(Product, name="sandwich", _create_files=True, category=self.category)

    def test_home_view_searched(self):
        response = self.client.get("/?searched=pizza")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["all_categories"]), 1)
        self.assertEqual(len(response.context["all_products"]), 1)
        self.assertIsInstance(response.context["form"], CartAddForm)
        self.assertIsInstance(response.context["page_data"], PageData)

    def test_home_view_not_searched(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["all_categories"]), 1)
        self.assertEqual(len(response.context["all_products"]), 2)
        self.assertIsInstance(response.context["form"], CartAddForm)
        self.assertIsInstance(response.context["page_data"], PageData)

    def tearDown(self):
        self.product1.delete()
        self.product2.delete()
        self.category.delete() 

class ProductDetailViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product1 = baker.make(Product, name="pizza", _create_files=True)

    def test_product_detail_get(self):
        url = reverse("cafe:product_detail", args=[self.product1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cafe/product_detail.html")
        self.assertIsInstance(response.context["product"], Product)
        self.assertIsInstance(response.context["form"], CartAddForm)

    def tearDown(self):
        self.product1.delete()

class AboutViewTest(TestCase):
    def test_about_view_get(self):
        url = reverse("cafe:about")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cafe/about.html")


class ContactViewTest(TestCase):
    def test_about_view_get(self):
        url = reverse("cafe:contact")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cafe/contact.html")

    def test_about_view_post(self):
        data = {
            "name": "mahdi",
            "email": "mahdi@gmail.com",
            "subject": "test",
            "message": "test message",
        }
        url = reverse("cafe:contact")
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("cafe:home"))

