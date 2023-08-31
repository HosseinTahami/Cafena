from django.test import TestCase
from ..utils_dashboard import (
    MostSellerProducts,
    OrdersManager,
    BestCustomer,
    ComparisonOrders,
    ComparisonCustomers,
    MostSellerCategories,
)
from model_bakery import baker
from cafe.models import Product, Category
from orders.models import Order, OrderItem
import datetime
import json
import pytz
from ..models import Customer


class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.now = datetime.datetime.now(tz=pytz.timezone("Asia/Tehran"))
        today = cls.now.replace(hour=0, minute=0, second=1, microsecond=0)
        morning_time = datetime.time(9, 0)
        noon_time = datetime.time(13, 0)
        night_time = datetime.time(20, 0)
        last_year = today - datetime.timedelta(days=366)
        last_month = today - datetime.timedelta(days=32)
        last_week = today - datetime.timedelta(days=8)
        yesterday = today - datetime.timedelta(days=1)
        morning_today = datetime.datetime.combine(today.date(), morning_time)
        noon_today = datetime.datetime.combine(today.date(), noon_time)
        night_today = datetime.datetime.combine(today.date(), night_time)

        cls.category1 = baker.make(Category, id=1, name="fastfood", _create_files=True)
        cls.category2 = baker.make(Category, id=2, name="hotdrink", _create_files=True)
        cls.category3 = baker.make(Category, id=3, name="colddrink", _create_files=True)
        cls.category4 = baker.make(Category, id=4, name="breakfast", _create_files=True)
        cls.category5 = baker.make(Category, id=5, name="irani", _create_files=True)

        cls.product1 = baker.make(
            Product, id=1, category=cls.category1, _create_files=True
        )
        cls.product2 = baker.make(
            Product, id=2, category=cls.category2, _create_files=True
        )
        cls.product3 = baker.make(
            Product, id=3, category=cls.category3, _create_files=True
        )
        cls.product4 = baker.make(
            Product, id=4, category=cls.category4, _create_files=True
        )
        cls.product5 = baker.make(
            Product, id=5, category=cls.category5, _create_files=True
        )
        cls.product6 = baker.make(
            Product, id=6, category=cls.category1, name="pizza", _create_files=True
        )
        cls.product7 = baker.make(
            Product,
            id=7,
            category=cls.category2,
            name="burger",
            price=20,
            _create_files=True,
        )
        cls.product8 = baker.make(
            Product,
            id=8,
            category=cls.category3,
            name="sandwich",
            price=10,
            _create_files=True,
        )

        cls.customer1 = baker.make(Customer, id=1, phone_number="09121111111")
        cls.customer1.joined = last_year
        cls.customer1.save()
        cls.customer2 = baker.make(Customer, id=2, phone_number="09122222222")
        cls.customer2.joined = last_month
        cls.customer2.save()
        cls.customer3 = baker.make(Customer, id=3, phone_number="09123333333")
        cls.customer3.joined = last_week
        cls.customer3.save()
        cls.customer4 = baker.make(Customer, id=4, phone_number="09124444444")
        cls.customer4.joined = yesterday
        cls.customer4.save()
        cls.customer5 = baker.make(Customer, id=5, phone_number="09125555555")
        cls.customer5.joined = today
        cls.customer5.save()

        cls.order1 = baker.make(
            Order, id=1, customer=cls.customer1, paid=True, status="a"
        )
        cls.order1.create_time = last_year
        cls.order1.save()
        cls.order2 = baker.make(
            Order, id=2, customer=cls.customer2, paid=True, status="a"
        )
        cls.order2.create_time = last_month
        cls.order2.save()
        cls.order3 = baker.make(
            Order, id=3, customer=cls.customer3, paid=True, status="a"
        )
        cls.order3.create_time = last_week
        cls.order3.save()
        cls.order4 = baker.make(
            Order, id=4, customer=cls.customer4, paid=True, status="a"
        )
        cls.order4.create_time = yesterday
        cls.order4.save()
        cls.order5 = baker.make(
            Order, id=5, customer=cls.customer5, paid=True, status="a"
        )
        cls.order5.create_time = today
        cls.order5.save()
        cls.order6 = baker.make(Order, id=6, customer=cls.customer1)
        cls.order6.create_time = morning_today
        cls.order6.save()
        cls.order7 = baker.make(Order, id=7, customer=cls.customer2)
        cls.order7.create_time = noon_today
        cls.order7.save()
        cls.order8 = baker.make(Order, id=8, customer=cls.customer3)
        cls.order8.create_time = night_today
        cls.order8.save()

        cls.orderitem1 = baker.make(
            OrderItem, product=cls.product1, order=cls.order1, quantity=50, price=10
        )
        cls.orderitem2 = baker.make(
            OrderItem, product=cls.product2, order=cls.order2, quantity=40, price=10
        )
        cls.orderitem3 = baker.make(
            OrderItem, product=cls.product3, order=cls.order3, quantity=30, price=10
        )
        cls.orderitem4 = baker.make(
            OrderItem, product=cls.product4, order=cls.order4, quantity=20, price=10
        )
        cls.orderitem5 = baker.make(
            OrderItem, product=cls.product5, order=cls.order5, quantity=10, price=10
        )
        cls.orderitem6 = baker.make(
            OrderItem, product=cls.product6, order=cls.order6, quantity=3, price=10
        )
        cls.orderitem7 = baker.make(
            OrderItem, product=cls.product7, order=cls.order7, quantity=2, price=10
        )
        cls.orderitem8 = baker.make(
            OrderItem, product=cls.product8, order=cls.order8, quantity=1, price=10
        )
        cls.orderitem9 = baker.make(
            OrderItem, product=cls.product7, order=cls.order8, quantity=1, price=20
        )


class MostSellerProductsTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.most_seller = MostSellerProducts(3)

    def test_most_seller_products_all(self):
        product_dict = self.most_seller.most_seller_products_all()
        values = list(product_dict.values())
        self.assertEqual(values[0][0], 1)
        self.assertEqual(values[1][0], 2)
        self.assertEqual(values[2][0], 3)

    def test_most_seller_products_year(self):
        product_dict = self.most_seller.most_seller_products_year()
        values = list(product_dict.values())
        self.assertEqual(values[0][0], 2)
        self.assertEqual(values[1][0], 3)
        self.assertEqual(values[2][0], 4)

    def test_most_seller_products_month(self):
        product_dict = self.most_seller.most_seller_products_month()
        values = list(product_dict.values())
        self.assertEqual(values[0][0], 3)
        self.assertEqual(values[1][0], 4)
        self.assertEqual(values[2][0], 5)

    def test_most_seller_products_week(self):
        product_dict = self.most_seller.most_seller_products_week()
        values = list(product_dict.values())
        self.assertEqual(values[0][0], 4)
        self.assertEqual(values[1][0], 5)
        self.assertEqual(values[2][0], 6)

    def test_most_seller_products_today(self):
        product_dict = self.most_seller.most_seller_products_today()
        values = list(product_dict.values())
        self.assertEqual(values[0][0], 5)
        self.assertEqual(values[1][0], 6)
        self.assertEqual(values[2][0], 7)

    def test_most_seller_products_custom(self):
        product_dict = self.most_seller.most_seller_products_custom(
            date1=self.now.date() - datetime.timedelta(days=10), date2=self.now.date()
        )
        values = list(product_dict.values())
        self.assertEqual(values[0][0], 3)
        self.assertEqual(values[1][0], 4)
        self.assertEqual(values[2][0], 5)

    def test_most_seller_products_morning(self):
        product_json = self.most_seller.most_seller_products_morning()
        product_dict = json.loads(product_json)
        self.assertEqual(product_dict["pizza"], 3)
        self.assertEqual(product_dict["other"], 0)
        self.assertEqual(len(list(product_dict.values())), 2)

    def test_most_seller_products_noon(self):
        product_json = self.most_seller.most_seller_products_noon()
        product_dict = json.loads(product_json)
        self.assertEqual(product_dict["burger"], 2)
        self.assertEqual(product_dict["other"], 0)
        self.assertEqual(len(list(product_dict.values())), 2)

    def test_most_seller_products_night(self):
        product_json = self.most_seller.most_seller_products_night()
        product_dict = json.loads(product_json)
        self.assertEqual(product_dict["sandwich"], 1)
        self.assertEqual(product_dict["burger"], 1)
        self.assertEqual(product_dict["other"], 0)
        self.assertEqual(len(list(product_dict.values())), 3)

    def test_most_seller_products_custom_by_hour(self):
        product_json = self.most_seller.most_seller_products_custom_by_hour(
            hour1=8, hour2=12
        )
        product_dict = json.loads(product_json)
        # print(product_dict)
        # self.assertEqual(product_dict["pizza"], 3)
        self.assertEqual(product_dict["other"], 0)


class OrderManagerTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.order_manager = OrdersManager()

    def test_this_year_orders(self):
        this_year_orders = self.order_manager.this_year_orders()
        this_year_orders_list = list(this_year_orders)
        self.assertAlmostEquals(len(this_year_orders_list), 4)

    def test_this_month_orders(self):
        this_month_orders = self.order_manager.this_month_orders()
        this_month_orders_list = list(this_month_orders)
        self.assertAlmostEquals(len(this_month_orders_list), 3)

    def test_this_week_orders(self):
        this_week_orders = self.order_manager.this_week_orders()
        this_week_orders_list = list(this_week_orders)
        self.assertAlmostEquals(len(this_week_orders_list), 2)

    def test_yesterday_orders(self):
        this_yesterday_orders = self.order_manager.yesterday_orders()
        this_yesterday_orders_list = list(this_yesterday_orders)
        self.assertAlmostEquals(len(this_yesterday_orders_list), 1)

    def test_today_orders(self):
        this_today_orders = self.order_manager.today_orders()
        this_today_orders_list = list(this_today_orders)
        self.assertAlmostEquals(len(this_today_orders_list), 1)

    def test_orders_with_cost(self):
        orders_with_cost = list(
            self.order_manager.orders_with_costs(orders=self.order8)
        )
        self.assertEquals(orders_with_cost[0][1], 30)

    def test_orders_with_cost_custom(self):
        orders_with_cost_custom = list(
            self.order_manager.orders_with_costs_custom(
                date1=self.now.date() - datetime.timedelta(days=10),
                date2=self.now.date(),
            )
        )
        self.assertEquals(len(orders_with_cost_custom), 6)
        self.assertEquals(len(orders_with_cost_custom[0]), 2)

    def test_peak_business_hours(self):
        each_hour = self.order_manager.get_peak_business_hours()
        each_hour_dict = json.loads(each_hour)
        self.assertEqual(each_hour_dict["0"], 1)
        self.assertEqual(len(list(each_hour_dict.items())), 18)

    def test_count_by_status(self):
        order9 = baker.make(Order, id=9, customer=self.customer4)
        order9.status = "r"
        order9.create_time = self.now
        order9.save()
        status_js = self.order_manager.get_count_by_status()
        status_dict = json.loads(status_js)
        self.assertEqual(status_dict["accepted"], 1)
        self.assertEqual(status_dict["pending"], 3)
        self.assertEqual(status_dict["rejected"], 1)
        order9.delete()

    # def test_count_by_personnel(self):
    #     each_personnel_json = self.order_manager.get_personnel_count_by_date()
    #     each_personnel_dict = json.loads(each_personnel_json)
    #     print("each personnel:", each_personnel_dict)


class BestCustomerTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.best_customer = BestCustomer(3)

    def test_best_customer_all(self):
        best_customers_all = self.best_customer.best_customers_all()
        self.assertEqual(best_customers_all[0][0], "09121111111")
        self.assertEqual(best_customers_all[1][0], "09122222222")
        self.assertEqual(best_customers_all[2][0], "09123333333")

    def test_best_customer_year(self):
        best_customers_year = self.best_customer.best_customers_year()
        self.assertEqual(best_customers_year[0][0], "09122222222")
        self.assertEqual(best_customers_year[1][0], "09123333333")
        self.assertEqual(best_customers_year[2][0], "09124444444")

    def test_best_customer_month(self):
        best_customers_month = self.best_customer.best_customers_month()
        self.assertEqual(best_customers_month[0][0], "09123333333")
        self.assertEqual(best_customers_month[1][0], "09124444444")
        self.assertEqual(best_customers_month[2][0], "09125555555")

    def test_best_customer_week(self):
        best_customers_week = self.best_customer.best_customers_week()
        self.assertEqual(best_customers_week[0][0], "09124444444")
        self.assertEqual(best_customers_week[1][0], "09125555555")

    def test_best_customer_custom(self):
        best_customers_custom = self.best_customer.best_customers_custom(
            date1=self.now.date() - datetime.timedelta(days=10), date2=self.now.date()
        )
        self.assertEqual(best_customers_custom[0][0], "09123333333")
        self.assertEqual(best_customers_custom[1][0], "09124444444")
        self.assertEqual(best_customers_custom[2][0], "09125555555")


class ComparisonOrdersTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.compare_orders = ComparisonOrders()

    def test_compare_order_annual(self):
        compare_annual = self.compare_orders.compare_order_annual()
        self.assertEqual(compare_annual["current"], 4)
        self.assertEqual(compare_annual["last"], 1)
        self.assertEqual(compare_annual["changes_percentage"], 300.00)
        self.assertEqual(compare_annual["changes_number"], 3)

    def test_compare_order_monthly(self):
        compare_monthly = self.compare_orders.compare_order_monthly()
        self.assertEqual(compare_monthly["current"], 3)
        self.assertEqual(compare_monthly["last"], 1)
        self.assertEqual(compare_monthly["changes_percentage"], 200.00)
        self.assertEqual(compare_monthly["changes_number"], 2)

    def test_compare_order_weekly(self):
        compare_weekly = self.compare_orders.compare_order_weekly()
        self.assertEqual(compare_weekly["current"], 2)
        self.assertEqual(compare_weekly["last"], 1)
        self.assertEqual(compare_weekly["changes_percentage"], 100.00)
        self.assertEqual(compare_weekly["changes_number"], 1)

    def test_compare_order_daily(self):
        compare_daily = self.compare_orders.compare_order_daily()
        self.assertEqual(compare_daily["current"], 1)
        self.assertEqual(compare_daily["last"], 1)
        self.assertEqual(compare_daily["changes_percentage"], 0)
        self.assertEqual(compare_daily["changes_number"], 0)


class ComparisonCustomersTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.compare_customers = ComparisonCustomers()

    def test_compare_customer_annual(self):
        compare_annual = self.compare_customers.compare_customer_annual()
        self.assertEqual(compare_annual["current"], 4)
        self.assertEqual(compare_annual["last"], 1)
        self.assertEqual(compare_annual["changes_percentage"], 300.00)
        self.assertEqual(compare_annual["changes_number"], 3)

    def test_compare_customer_monthly(self):
        compare_monthly = self.compare_customers.compare_customer_monthly()
        self.assertEqual(compare_monthly["current"], 3)
        self.assertEqual(compare_monthly["last"], 1)
        self.assertEqual(compare_monthly["changes_percentage"], 200.00)
        self.assertEqual(compare_monthly["changes_number"], 2)

    def test_compare_customer_weekly(self):
        compare_weekly = self.compare_customers.compare_customer_weekly()
        self.assertEqual(compare_weekly["current"], 2)
        self.assertEqual(compare_weekly["last"], 1)
        self.assertEqual(compare_weekly["changes_percentage"], 100.00)
        self.assertEqual(compare_weekly["changes_number"], 1)

    def test_compare_customer_daily(self):
        compare_daily = self.compare_customers.compare_customer_daily()
        self.assertEqual(compare_daily["current"], 1)
        self.assertEqual(compare_daily["last"], 1)
        self.assertEqual(compare_daily["changes_percentage"], 0)
        self.assertEqual(compare_daily["changes_number"], 0)


class MostSellerCategoriesTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.most_seller_categories = MostSellerCategories(3)

    def test_most_seller_categories_all(self):
        category_json = self.most_seller_categories.most_seller_categories_all()
        category_dict = json.loads(category_json)
        self.assertEqual(category_dict["fastfood"], 53)
        self.assertEqual(category_dict["hotdrink"], 43)
        self.assertEqual(category_dict["colddrink"], 31)

    def test_most_seller_categories_year(self):
        category_json = self.most_seller_categories.most_seller_categories_year()
        category_dict = json.loads(category_json)
        self.assertEqual(category_dict["hotdrink"], 43)
        self.assertEqual(category_dict["colddrink"], 31)
        self.assertEqual(category_dict["breakfast"], 20)

    def test_most_seller_categories_month(self):
        category_json = self.most_seller_categories.most_seller_categories_month()
        category_dict = json.loads(category_json)
        self.assertEqual(category_dict["colddrink"], 31)
        self.assertEqual(category_dict["breakfast"], 20)
        self.assertEqual(category_dict["irani"], 10)

    def test_most_seller_categories_week(self):
        category_json = self.most_seller_categories.most_seller_categories_week()
        category_dict = json.loads(category_json)
        self.assertEqual(category_dict["breakfast"], 20)
        self.assertEqual(category_dict["irani"], 10)
        self.assertEqual(category_dict["hotdrink"], 3)

    def test_most_seller_categories_custom(self):
        category_json = self.most_seller_categories.most_seller_categories_custom(
            date1=self.now.date() - datetime.timedelta(days=10), date2=self.now.date()
        )
        category_dict = json.loads(category_json)
        self.assertEqual(category_dict["colddrink"], 31)
        self.assertEqual(category_dict["breakfast"], 20)
        self.assertEqual(category_dict["irani"], 10)
