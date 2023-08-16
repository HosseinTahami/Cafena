from django.db.models import Sum, Count
from cafe.models import Product, Category
from accounts.models import Customer
from orders.models import Order
import datetime
import json
from dataclasses import dataclass


@dataclass
class DateVars:
    current_date: datetime = datetime.datetime.now().date()
    last_date: datetime = datetime.datetime.now().date() - datetime.timedelta(days=1)

    @classmethod
    def get_current_year(cls):
        return cls.current_date.year

    @classmethod
    def get_last_year(cls):
        return cls.current_date.year - 1

    @classmethod
    def get_first_day_current_month(cls):
        return cls.current_date.replace(day=1)

    @classmethod
    def get_last_day_last_month(cls):
        return cls.current_date.replace(day=1) - datetime.timedelta(days=1)

    @classmethod
    def get_first_day_last_month(cls):
        last_day_last_month = cls.get_last_day_last_month()
        return last_day_last_month.replace(day=1)

    @classmethod
    def get_first_day_current_week(cls):
        first_day_current_week = cls.current_date - datetime.timedelta(
            days=cls.current_date.weekday()
        )
        return first_day_current_week

    @classmethod
    def get_last_day_last_week(cls):
        last_day_last_week = cls.get_first_day_current_week() - datetime.timedelta(
            days=1
        )
        return last_day_last_week

    @classmethod
    def get_first_day_last_week(cls):
        first_day_last_week = cls.get_last_day_last_week() - datetime.timedelta(days=6)
        return first_day_last_week


class MostSellerProducts:
    def most_seller_products_all(self, number):
        filtered_products = Product.objects.all()
        return self.count_quantity(filtered_products, number)

    def most_seller_products_year(self, number):
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__year=DateVars.get_current_year()
        )
        return self.count_quantity(filtered_products, number)

    def most_seller_products_month(self, number):
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__date__gte=DateVars.get_first_day_current_month()
        )
        return self.count_quantity(filtered_products, number)

    def most_seller_products_week(self, number):
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__date__gte=DateVars.get_first_day_current_week()
        )
        return self.count_quantity(filtered_products, number)

    def most_seller_products_today(self, number):
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__date=DateVars.current_date
        )
        return self.count_quantity(filtered_products, number)

    def count_quantity(self, filtered_products, number):
        products = filtered_products.annotate(
            total_quantity=Sum("orderitem__quantity")
        ).order_by("-total_quantity")[:number]
        products_dict = self.to_dict(products)
        return products_dict

    def to_dict(self, most_sellar):
        product_quantity = {}
        for product in most_sellar:
            product_quantity[product.name] = [
                product.id,
                product.image.url,
                product.name,
                product.total_quantity,
                float(product.price),
                float(product.price) * product.total_quantity,
            ]
        return product_quantity

    def to_json(self, products_dict):
        return json.dumps(products_dict)


class OrdersManager:
    def __init__(self):
        self.orders = Order.objects.all().order_by("-create_time")
        self.paid_orders = Order.objects.filter(paid=True).order_by("-create_time")

    def this_year_orders(self):
        this_year_orders = self.paid_orders.filter(
            created_at__year=DateVars.get_current_year()
        )
        return this_year_orders

    def this_month_orders(self):
        this_month_orders = self.paid_orders.filter(
            created_at__date__gte=DateVars.get_first_day_current_month()
        )
        return this_month_orders

    def this_week_orders(self):
        this_week_orders = self.paid_orders.objects.filter(
            created_at__date__gte=DateVars.get_first_day_current_week()
        )
        return this_week_orders

    def yesterday_orders(self):
        yesterday_orders = self.paid_orders.objects.filter(
            created_at__date=DateVars.last_date
        )
        return yesterday_orders

    def today_orders(self):
        today_orders = self.paid_orders.objects.filter(
            created_at__date=DateVars.current_date
        )
        return today_orders

    def get_every_hour_orders(self, hour):
        first_hour = DateVars.current_date.replace(hour=hour)
        second_hour = DateVars.current_date.replace(hour=hour + 1)
        every_hour_orders_count = self.paid_orders.objects.filter(
            created_at__range=(first_hour, second_hour)
        ).count()
        return every_hour_orders_count

    def orders_with_costs(self, orders=None):
        total_price = []
        if not orders:
            orders = self.orders
        for order in orders:
            total_price.append(order.get_total_price())
        orders_with_costs = zip(self.orders, total_price)
        return orders_with_costs

    def total_sales(self):
        return sum(paid_order.get_total_price() for paid_order in self.paid_orders)

    def count_orders(self):
        return self.paid_orders.count()


class BestCustomer:
    def best_customers_all(self):
        orders = Order.objects.all()
        best_customers_all = {}
        return self.add_best_customer(orders, best_customers_all)

    def best_customers_year(self):
        orders = Order.objects.filter(create_time__year=DateVars.get_current_year())
        best_customers_year = {}
        return self.add_best_customer(orders, best_customers_year)

    def best_customers_month(self):
        orders = Order.objects.filter(
            create_time__date__gte=DateVars.get_first_day_current_month()
        )
        best_customers_month = {}
        return self.add_best_customer(orders, best_customers_month)

    def best_customers_week(self):
        orders = Order.objects.filter(
            create_time__date__gte=DateVars.get_first_day_current_week()
        )
        best_customers_month = {}
        return self.add_best_customer(orders, best_customers_month)

    def add_best_customer(self, orders, best_customers):
        for order in orders:
            if best_customers.get(order.customer.phone_number):
                best_customers[order.customer.phone_number] += order.get_total_price()
            else:
                best_customers[order.customer.phone_number] = order.get_total_price()
        return best_customers

    def count_customers(self):
        return Customer.objects.count()


class Comparison:
    def get_change_percenatge(self, current, last):
        return (current - last) / last

    def return_dictionary(self, current, last):
        return {
            "current": current,
            "last": last,
            "changes_percentage": self.get_change_percenatge(current, last),
            "changes_numebr": current - last,
        }


class ComparisonOrders(Comparison):
    def __init__(self):
        self.orders = Order.objects.all().order_by("-create_time")
        self.paid_orders = Order.objects.filter(paid=True).order_by("-create_time")

    def compare_order_daily(self):
        current_date_orders_count = self.paid_orders.objects.filter(
            created_at__date=DateVars.current_date
        ).count()
        last_date_orders_count = self.paid_orders.objects.filter(
            created_at__date=DateVars.last_date
        ).count()
        return self.return_dictionary(current_date_orders_count, last_date_orders_count)

    def compare_order_weekly(self):
        last_week_orders_count = self.paid_orders.filter(
            created_at__range=(
                DateVars.get_first_day_last_week(),
                DateVars.get_last_day_last_week(),
            )
        ).count()
        current_week_orders_count = self.paid_orders.filter(
            created_at__range=(
                DateVars.get_first_day_current_week(),
                DateVars.current_date,
            )
        ).count()

        return self.return_dictionary(current_week_orders_count, last_week_orders_count)

    def compare_order_monthly(self):
        last_month_orders_count = self.paid_orders.filter(
            created_at__range=(
                DateVars.get_first_day_last_month(),
                DateVars.get_last_day_last_month(),
            )
        ).count()
        current_month_orders_count = self.paid_orders.filter(
            created_at__range=(
                DateVars.get_first_day_current_month,
                DateVars.current_date,
            )
        ).count()
        return self.return_dictionary(
            current_month_orders_count, last_month_orders_count
        )

    def compare_order_annual(self):
        last_year_orders_count = self.paid_orders.objects.filter(
            created_at__year=DateVars.get_last_year()
        ).count()
        current_year_orders_count = self.paid_orders.objects.filter(
            created_at__year=DateVars.get_current_year()
        ).count()
        return self.return_dictionary(current_year_orders_count, last_year_orders_count)


class ComparisonCustomers(Comparison):
    def __init__(self):
        self.customers = Customer.objects.all().order_by("-joined")

    def compare_customer_daily(self):
        current_date_customers_count = self.customers.objects.filter(
            joined__date=DateVars.current_date
        ).count()
        last_date_customers_count = self.customers.objects.filter(
            joined__date=DateVars.last_date
        ).count()
        return self.return_dictionary(
            current_date_customers_count, last_date_customers_count
        )

    def compare_customer_weekly(self):
        last_week_customers_count = self.customers.filter(
            joined__range=(
                DateVars.get_first_day_last_week(),
                DateVars.get_last_day_last_week(),
            )
        ).count()
        current_week_customers_count = self.customers.filter(
            joined__range=(
                DateVars.get_first_day_current_week(),
                DateVars.current_date,
            )
        ).count()

        return self.return_dictionary(
            current_week_customers_count, last_week_customers_count
        )

    def compare_customer_monthly(self):
        last_month_customers_count = self.customers.filter(
            joined__range=(
                DateVars.get_first_day_last_month(),
                DateVars.get_last_day_last_month(),
            )
        ).count()
        current_month_customers_count = self.customers.filter(
            joined__range=(
                DateVars.get_first_day_current_month,
                DateVars.current_date,
            )
        ).count()
        return self.return_dictionary(
            current_month_customers_count, last_month_customers_count
        )

    def compare_customer_annual(self):
        last_year_customers_count = self.customers.objects.filter(
            joined__year=DateVars.get_last_year()
        ).count()
        current_year_customers_count = self.customers.objects.filter(
            joined__year=DateVars.get_current_year()
        ).count()
        return self.return_dictionary(
            current_year_customers_count, last_year_customers_count
        )


class MostSellerCategories:
    def most_seller_products_all(self, number):
        filtered_categories = Category.objects.all()
        return self.count_quantity(filtered_categories, number)

    def most_seller_categories_year(self, number):
        filtered_categories = Category.objects.filter(
            product__orderitem__order__create_time__year=DateVars.get_current_year()
        )
        return self.count_quantity(filtered_categories, number)

    def most_seller_categories_month(self, number):
        filtered_categories = Category.objects.filter(
            product__orderitem__order__create_time__date__gte=DateVars.get_first_day_current_month()
        )
        return self.count_quantity(filtered_categories, number)

    def most_seller_categories_week(self, number):
        filtered_categories = Category.objects.filter(
            product__orderitem__order__create_time__date__gte=DateVars.get_first_day_current_week()
        )
        return self.count_quantity(filtered_categories, number)

    def most_seller_categories_today(self, number):
        filtered_categories = Category.objects.filter(
            product__orderitem__order__create_time__date=DateVars.current_date
        )
        return self.count_quantity(filtered_categories, number)

    def count_quantity(self, filtered_categories, number):
        categories = filtered_categories.annotate(
            total_quantity=Sum("product__orderitem__quantity")
        ).order_by("-total_quantity")[:number]
        products_dict = self.to_dict(categories)
        return products_dict

    def to_dict(self, most_sellar):
        category_quantity = {}
        for category in most_sellar:
            category_quantity[category.name] = [
                category.id,
                category.image.url,
                category.name,
                category.total_quantity,
            ]
        return category_quantity

    def to_json(self, products_dict):
        return json.dumps(products_dict)
