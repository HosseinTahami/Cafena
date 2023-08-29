from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from cafe.models import Category, Product
from orders.forms import CartAddForm
from dynamic.models import PageData
from cafe.views import HomeView, ProductDetailView
from model_bakery import baker

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
