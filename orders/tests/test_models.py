from django.test import TestCase
from orders.models import Order, OrderItem, Table
from cafe.models import Product
from model_bakery import baker
from accounts.models import Customer, Personnel


class TestOrderModel(TestCase):
    def setUp(self):
        self.customer = baker.make(Customer, name="Test Customer")
        self.personnel = baker.make(Personnel, full_name="Test Personnel")
        self.table = baker.make(Table, table_number=1)
        self.order = baker.make(
            Order,
            status="p",
            # create_time="2023-08-19 17:41:43.919259+00:00",
            customer=self.customer,
            personnel=self.personnel,
            table=self.table,
        )
        self.order.create_time = '2023-08-19 17:41:43.919259+00:00'
        self.product1 = baker.make(
            Product, name="Test Product 1", price=10.0, _create_files=True
        )
        self.product2 = baker.make(
            Product, name="Test Product 2", price=20.0, _create_files=True
        )
        self.order_item1 = baker.make(
            OrderItem,
            order=self.order,
            product=self.product1,
            quantity=2,
            price=self.product1.price,
        )
        self.order_item2 = baker.make(
            OrderItem,
            order=self.order,
            product=self.product2,
            quantity=1,
            price=self.product2.price,
        )

    def test_get_total_price(self):
        expected_total_price = (self.order_item1.price * self.order_item1.quantity) + (
            self.order_item2.price * self.order_item2.quantity
        )
        self.assertEqual(self.order.get_total_price(), expected_total_price)

    def test_str_method(self):
        expected_str = "p || 2023-08-19 17:41:43.919259+00:00"
        self.assertEqual(str(self.order), expected_str)


class TestOrderItemModel(TestCase):
    def setUp(self):
        customer = baker.make(Customer, name="Test Customer")
        personnel = baker.make(Personnel, full_name="Test Personnel")
        table = baker.make(Table, table_number=1)
        order = baker.make(
            Order,
            status="p",
            create_time="2023-08-19 17:41:43.919259+00:00",
            customer=customer,
            personnel=personnel,
            table=table,
        )
        product = baker.make(
            Product, name="Test Product", price=10.0, _create_files=True
        )
        self.order_item = baker.make(
            OrderItem, order=order, product=product, quantity=2, price=product.price
        )

    def test_model_orderitem_get_cost(self):
        expected_str = self.order_item.price * self.order_item.quantity
        self.assertEqual(self.order_item.get_cost(), expected_str)

    def test_model_orderitem_str(self):
        expected_str = f"{self.order_item.product} || {self.order_item.quantity}"
        self.assertEqual(str(self.order_item), expected_str)
