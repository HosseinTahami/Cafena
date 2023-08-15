from django.db.models import Sum, Count
from cafe.models import Product
from accounts.models import Customer
from orders.models import Order
import datetime
import json
from dataclasses import dataclass


@dataclass
class DateVars:
    current_date: datetime = datetime.datetime.now().date()
    current_year: int = datetime.datetime.now().year
    last_year: int = datetime.datetime.now().year - 1

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
        first_day_current_week = cls.current_date - datetime.timedelta(days=cls.current_date.weekday())
        return first_day_current_week
    
    @classmethod
    def get_last_day_last_week(cls):
        last_day_last_week = cls.get_first_day_current_week() - datetime.timedelta(days=1)
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
        current_year = datetime.datetime.now().year
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__year=current_year
        )
        return self.count_quantity(filtered_products, number)

    def most_seller_products_month(self, number):
        current_date = datetime.datetime.now().date()
        first_day_month = current_date.replace(day=1)
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__date__gte=first_day_month
        )
        return self.count_quantity(filtered_products, number)

    def most_seller_products_week(self, number):
        current_date = datetime.datetime.now().date()
        start_of_week = current_date - datetime.timedelta(days=current_date.weekday())
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__date__gte=start_of_week
        )
        return self.count_quantity(filtered_products, number)

    def most_seller_products_today(self, number):
        current_date = datetime.datetime.now().date()
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__date=current_date
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
        current_year = datetime.datetime.now().year
        this_year_orders = self.paid_orders.filter(created_at__year=current_year)
        return this_year_orders

    def this_month_orders(self):
        current_month = datetime.datetime.now().month
        this_month_orders = self.paid_orders.filter(created_at__month=current_month)
        return this_month_orders

    def this_week_orders(self):
        current_date = datetime.now().date()
        start_of_week = current_date - datetime.timedelta(days=current_date.weekday())
        this_week_orders = self.paid_orders.objects.filter(
            created_at__date__gte=start_of_week
        )
        return this_week_orders

    def today_orders(self):
        current_date = datetime.now().date()
        today_orders = self.paid_orders.objects.filter(created_at__date=current_date)
        return today_orders

    def orders_with_costs(self):
        total_price = []
        for order in self.orders:
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
        current_year = datetime.datetime.now().year
        orders = Order.objects.filter(create_time=current_year)
        best_customers_year = {}
        return self.add_best_customer(orders, best_customers_year)

    def best_customers_month(self):
        current_month = datetime.datetime.now().month
        orders = Order.objects.filter(create_time=current_month)
        best_customers_month = {}
        return self.add_best_customer(orders, best_customers_month)

    def best_customers_week(self):
        current_month = datetime.datetime.now().date()
        orders = Order.objects.filter(create_time=current_month)
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
    def __init__(self):
        self.orders = Order.objects.all().order_by("-create_time")
        self.paid_orders = Order.objects.filter(paid=True).order_by("-create_time")

    def compare_order_daily(self):
        current_date = datetime.datetime.now().date()
        last_date = current_date - datetime.timedelta(days=1)
        current_date_orders_count = self.paid_orders.objects.filter(
            created_at__date=current_date
        ).count()
        last_date_orders_count = self.paid_orders.objects.filter(
            created_at__date=last_date
        ).count()
        return {
            "current_date_orders_count": current_date_orders_count,
            "last_date_orders_count": last_date_orders_count,
            "changes_percentage": self.get_change_percenatge(
                current_date_orders_count, last_date_orders_count
            ),
            "changes_numebr": current_date_orders_count - last_date_orders_count,
        }

    def compare_order_weekly(self):
        current_date = datetime.datetime.now().date()
        first_day_current_week = current_date - datetime.timedelta(
            days=current_date.weekday()
        )
        last_day_last_week = first_day_current_week - datetime.timedelta(days=1)
        first_day_last_week = last_day_last_week - datetime.timedelta(days=6)
        last_week_orders_count = self.paid_orders.filter(
            created_at__range=(first_day_last_week, last_day_last_week)
        ).count()
        current_week_orders_count = self.paid_orders.filter(
            created_at__range=(first_day_current_week, current_date)
        ).count()

        return {
            "current_week_orders_count": current_week_orders_count,
            "last_week_orders_count": last_week_orders_count,
            "changes_percentage": self.get_change_percenatge(
                current_week_orders_count, last_week_orders_count
            ),
            "changes_numebr": current_week_orders_count - last_week_orders_count,
        }

    def compare_order_monthly(self):
        current_date = datetime.datetime.now().date()
        first_day_current_month = current_date.replace(day=1)
        last_day_last_month = first_day_current_month - datetime.timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)

        last_month_orders_count = self.paid_orders.filter(
            created_at__range=(first_day_last_month, last_day_last_month)
        ).count()
        current_month_orders_count = self.paid_orders.filter(
            created_at__range=(first_day_current_month, current_date)
        ).count()
        return {
            "current_month_orders_count": current_month_orders_count,
            "last_month_orders_count": last_month_orders_count,
            "changes_percentage": self.get_change_percenatge(
                current_month_orders_count, last_month_orders_count
            ),
            "changes_numebr": current_month_orders_count - last_month_orders_count,
        }

    def compare_order_annual(self):
        current_date = datetime.datetime.now().date()
        first_day_current_year = current_date.replace(day=1, month=1)
        last_day_last_year = first_day_current_year - datetime.timedelta(days=1)
        first_day_last_year = last_day_last_year.replace(day=1, month=1)
        last_year_orders_count = self.paid_orders.objects.filter(
            created_at__range=(first_day_last_year, last_day_last_year)
        ).count()
        current_year_orders_count = self.paid_orders.objects.filter(
            created_at__range=(first_day_current_year, current_date)
        ).count()
        return {
            "current_year_orders_count": current_year_orders_count,
            "last_year_orders_count": last_year_orders_count,
            "changes_percentage": self.get_change_percenatge(
                current_year_orders_count, last_year_orders_count
            ),
            "changes_numebr": current_year_orders_count - last_year_orders_count,
        }

    def get_change_percenatge(self, current, last):
        return (current - last) / last
