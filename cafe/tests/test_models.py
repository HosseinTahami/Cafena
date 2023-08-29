from django.test import TestCase
from cafe.models import Category ,Product
from model_bakery   import baker


class TestCategoryModel(TestCase):
    def test_model_category_str(self):
        category = baker.make(Category , name="amin")
        self.assertEqual(str(category), 'amin')


class TestProductModel(TestCase):
    def test_model_product_str(self):
        product = baker.make(Product , name="amin", _create_files=True)
        self.assertEqual(str(product), 'amin')