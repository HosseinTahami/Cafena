from django.test import TestCase, RequestFactory
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
        self.product = baker.make(Product, _create_files=True)

    
def test_home_view(self):
    url = reverse("your_actual_url_name_here")  # Replace with the actual URL name
    request = self.factory.get(url)
    response = HomeView.as_view()(request)

    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, "cafe/home.html")

    self.assertEqual(len(response.context["all_categories"]), 1)
    self.assertEqual(len(response.context["all_products"]), 1)
    self.assertIsInstance(response.context["form"], CartAddForm)
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
