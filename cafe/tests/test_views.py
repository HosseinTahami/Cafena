from django.test import TestCase, Client
from django.urls import reverse
from cafe.models import Category, Product
from orders.forms import CartAddForm

from model_bakery   import baker

class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category1 = baker.make(Category ,name="Category 1")
        self.category2 = baker.make(Category ,name="Category 2")
        self.product1 = baker.make(Product ,name="Product 1", price=10.0, category=self.category1)
        self.product2 = baker.make(Product ,name="Product 2", price=20.0, category=self.category1)
        self.product3 = baker.make(Product ,name="Product 3", price=30.0, category=self.category2)

    def test_home_GET(self):
        response = self.client.get(reverse("cafe:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cafe/home.html")
        self.assertIn("all_categories", response.context_data)
        self.assertIn("all_products", response.context_data)
        self.assertIn("form", response.context_data)
        self.assertIn("page_data", response.context_data)
        self.assertQuerysetEqual(
            response.context_data["all_categories"],
            [repr(self.category1), repr(self.category2)],
            ordered=False,
        )
        self.assertQuerysetEqual(
            response.context_data["all_products"],
            [repr(self.product1), repr(self.product2), repr(self.product3)],
            ordered=False,
        )
        self.assertIsInstance(response.context_data["form"], CartAddForm)


class SearchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.product1 = baker.make(Product ,name="Product 1", description="Description 1")
        self.product2 = baker.make(Product ,name="Product 2", description="Description 2")
        self.product3 = baker.make(Product ,name="Product 3", description="Description 3")

    def test_search_GET(self):
        url = reverse("cafe:search_results")
        response = self.client.get(url, {"searched": "Product"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cafe/search_results.html")
        self.assertIn("results", response.context)
        self.assertIn("page_data", response.context)
        self.assertQuerysetEqual(
            response.context["results"],
            [repr(self.product1), repr(self.product2), repr(self.product3)],
            ordered=False,
        )

class ProductDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = baker.make(Product,name="Product", description="Description", price=10.0)

    def test_product_detail_GET(self):
        url = reverse("cafe:product_detail", kwargs={"pk": self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cafe/product_detail.html")
        self.assertIn("product", response.context)
        self.assertIn("form", response.context)
        self.assertEqual(response.context["product"], self.product)
        self.assertEqual(response.context["form"].initial["quantity"], 1)