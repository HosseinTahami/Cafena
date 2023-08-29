from django.test import TestCase
from orders.models import Product
from accounts.utils_dashboard import MostSellerProducts
from model_bakery   import baker

class MostSellerProductsTest(TestCase):
    def setUp(self):
        self.product1 = baker.make(Product,name="Product 1", price=10.0, _create_files=True)
        self.product2 = baker.make(Product,name="Product 2", price=20.0, _create_files=True)
        self.product3 = baker.make(Product,name="Product 3", price=30.0, _create_files=True)
        self.product4 = baker.make(Product,name="Product 4", price=40.0, _create_files=True)
        self.product5 = baker.make(Product,name="Product 5", price=50.0, _create_files=True)

    def test_most_seller_products_all(self):
        most_seller = MostSellerProducts(3)
        #products_dict = most_seller.most_seller_products_all()
        # expected_dict = {
        #     "Product 5": [self.product5.pk, self.product5.image.url, "Product 5", 0, 50.0, 0.0],
        #     "Product 4": [self.product4.pk, self.product4.image.url, "Product 4", 0, 40.0, 0.0],
        #     "Product 3": [self.product3.pk, self.product3.image.url, "Product 3", 0, 30.0, 0.0],
        # }
        # self.assertDictEqual(products_dict, expected_dict)

    def test_most_seller_products_year(self):
        most_seller = MostSellerProducts(2)
        products_dict = most_seller.most_seller_products_year()
        # expected_dict = {
        #     "Product 5": [self.product5.pk, self.product5.image.url, "Product 5", 0, 50.0, 0.0],
        #     "Product 4": [self.product4.pk, self.product4.image.url, "Product 4", 0, 40.0, 0.0],
        # }
        # self.assertDictEqual(products_dict, expected_dict)

    def test_most_seller_products_month(self):
        most_seller = MostSellerProducts(1)
        products_dict = most_seller.most_seller_products_month()
        # expected_dict = {"Product 5": [self.product5.pk, self.product5.image.url, "Product 5", 0, 50.0, 0.0]}
        # self.assertDictEqual(products_dict, expected_dict)

    def test_most_seller_products_week(self):
        most_seller = MostSellerProducts(2)
        products_dict = most_seller.most_seller_products_week()
        # expected_dict = {
        #     "Product 5": [self.product5.pk, self.product5.image.url, "Product 5", 0, 50.0, 0.0],
        #     "Product 4": [self.product4.pk, self.product4.image.url, "Product 4", 0, 40.0, 0.0],
        # }
        # self.assertDictEqual(products_dict, expected_dict)

    def test_most_seller_products_today(self):
        most_seller = MostSellerProducts(3)
        products_dict = most_seller.most_seller_products_today()
        # expected_dict = {
        #     "Product 5": [self.product5.pk, self.product5.image.url, "Product 5", 0, 50.0, 0.0],
        #     "Product 4": [self.product4.pk, self.product4.image.url, "Product 4", 0, 40.0, 0.0],
        #     "Product 3": [self.product3.pk, self.product3.image.url, "Product 3", 0, 30.0, 0.0],
        # }
        # self.assertDictEqual(products_dict, expected_dict)

    def test_most_seller_products_morning(self):
        most_seller = MostSellerProducts(2)
        products_dict = most_seller.most_seller_products_morning()
        expected_dict = {"Product 5": 0, "Product 4": 0, "Product 3": 0}
        #self.assertDictEqual(products_dict, expected_dict)

    def test_most_seller_products_noon(self):
        most_seller = MostSellerProducts(1)
        products_dict = most_seller.most_seller_products_noon()
        expected_dict = {"Product 5": 0}
        #self.assertDictEqual(products_dict, expected_dict)

    def test_most_seller_products_night(self):
        most_seller = MostSellerProducts(2)
        products_dict = most_seller.most_seller_products_night()
        expected_dict = {"Product 5": 0, "Product 4": 0}
        #self.assertDictEqual(products_dict, expected_dict)