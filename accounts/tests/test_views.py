from django.test import TestCase, RequestFactory
from django.urls import reverse
from cafe.models import Category, Product
from orders.forms import CartAddForm
from dynamic.models import PageData
from cafe.views import HomeView, SearchView, ProductDetailView

class ViewsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
    
    def setUp(self):
        self.category = Category.objects.create(name="Test Category")
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            price=10.0,
        )
    
    def test_home_view(self):
        url = reverse("home")  # Replace with the actual URL name for HomeView
        request = self.factory.get(url)
        response = HomeView.as_view()(request)
    
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cafe/home.html")
    
        self.assertEqual(len(response.context["all_categories"]), 1)
        self.assertEqual(len(response.context["all_products"]), 1)
        self.assertIsInstance(response.context["form"], CartAddForm)
        self.assertIsInstance(response.context["page_data"], PageData)
    
    def test_search_view(self):
        url = reverse("search")  # Replace with the actual URL name for SearchView
        request = self.factory.get(url, {"searched": "Test"})
        response = SearchView.as_view()(request)
    
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cafe/search_results.html")
    
        self.assertIn("results", response.context)
        self.assertIsInstance(response.context["page_data"], PageData)
    
    def test_product_detail_view(self):
        url = reverse("product_detail", kwargs={"pk": self.product.pk})
        request = self.factory.get(url)
        response = ProductDetailView.as_view()(request, pk=self.product.pk)
    
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cafe/product_detail.html")
    
        self.assertIn("product", response.context)
        self.assertIsInstance(response.context["product"], Product)
        self.assertIsInstance(response.context["form"], CartAddForm)
    
    def tearDown(self):
        self.product.delete()
        self.category.delete()
