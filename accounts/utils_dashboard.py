from django.db.models import Sum, Count, Case, When, IntegerField
from django.db.models.functions import ExtractHour

from cafe.models import Product, Category
from accounts.models import Customer, Personnel
from orders.models import Order

import datetime
import json
from typing import List, Iterable
import pytz


def get_date_from_staff(request, query, date1, date2, number=None):
    if number:
        result = query(number)
    else:
        result = query()

    date1_ = request.GET.get(date1)
    date2_ = request.GET.get(date2)
    if date1 and date2 and number:
        result = query(number, date1_, date2_)
    elif date1 and date2:
        result = query(date1_, date2_)
    return result


class DateVars:
    current_date: datetime = datetime.datetime.now(
        tz=pytz.timezone("Asia/Tehran")
    ).date()
    last_date: datetime = current_date - datetime.timedelta(days=1)
    current_datetime: datetime = datetime.datetime.now(tz=pytz.timezone("Asia/Tehran"))

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
    def __init__(self, number) -> None:
        self.number = number

    def most_seller_products_all(self, number=None):
        if number == None:
            number = self.number
        filtered_products = Product.objects.all()
        products = self.count_quantity(filtered_products)
        products_dict = self.to_dict(products, number)
        return products_dict

    def most_seller_products_year(self, number=None):
        if number == None:
            number = self.number
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__year=DateVars.get_current_year()
        )
        products = self.count_quantity(filtered_products)
        products_dict = self.to_dict(products, number)
        return products_dict

    def most_seller_products_month(self, number=None):
        if number == None:
            number = self.number
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__date__gte=DateVars.get_first_day_current_month()
        )
        products = self.count_quantity(filtered_products)
        products_dict = self.to_dict(products, number)
        return products_dict

    def most_seller_products_week(self, number=None):
        if number == None:
            number = self.number
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__date__gte=DateVars.get_first_day_current_week()
        )
        products = self.count_quantity(filtered_products)
        products_dict = self.to_dict(products, number)
        return products_dict

    def most_seller_products_today(self, number=None):
        if number == None:
            number = self.number
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__date=DateVars.current_date
        )
        products = self.count_quantity(filtered_products)
        products_dict = self.to_dict(products, number)
        return products_dict

    def most_seller_products_morning(self, number=None):
        if number == None:
            number = self.number
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__hour__range=(6, 12)
        )
        products = self.count_quantity(filtered_products)
        products_dict = self.to_dict_count(products, number)
        return self.to_json(products_dict)

    def most_seller_products_noon(self, number=None):
        if number == None:
            number = self.number
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__hour__range=(12, 18)
        )
        products = self.count_quantity(filtered_products)
        products_dict = self.to_dict_count(products, number)
        return self.to_json(products_dict)

    def most_seller_products_night(self, number=None):
        if number == None:
            number = self.number
        filtered_products = Product.objects.filter(
            orderitem__order__create_time__hour__range=(18, 23)
        )
        products = self.count_quantity(filtered_products)
        products_dict = self.to_dict_count(products, number)
        return self.to_json(products_dict)

    def count_quantity(self, filtered_products):
        products = filtered_products.annotate(
            total_quantity=Sum("orderitem__quantity")
        ).order_by("-total_quantity")
        return products

    def to_dict(self, most_sellar, number):
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
        sliced_dict = {
            key: product_quantity[key] for key in list(product_quantity)[:number]
        }
        return sliced_dict

    def to_dict_count(self, most_sellar, number):
        product_quantity = {}
        for product in most_sellar:
            product_quantity[product.name] = product.total_quantity
        sliced_dict = {
            key: product_quantity[key] for key in list(product_quantity)[:number]
        }
        other = {key: product_quantity[key] for key in list(product_quantity)[number:]}
        print(other)
        print(sum(other.values()))
        sliced_dict["other"] = sum(other.values())
        return sliced_dict

    def to_json(self, products_dict):
        return json.dumps(products_dict)


class OrdersManager:
    def __init__(self):
        self.orders = (
            Order.objects.prefetch_related("orderitem_set")
            .all()
            .order_by("-create_time")
        )
        self.paid_orders = (
            Order.objects.prefetch_related("orderitem_set")
            .filter(paid=True)
            .order_by("-create_time")
        )

    def this_year_orders(self):
        this_year_orders = self.paid_orders.filter(
            create_time__year=DateVars.get_current_year()
        )
        return this_year_orders

    def this_month_orders(self):
        this_month_orders = self.paid_orders.filter(
            create_time__date__gte=DateVars.get_first_day_current_month()
        )
        return this_month_orders

    def this_week_orders(self):
        this_week_orders = self.paid_orders.filter(
            create_time__date__gte=DateVars.get_first_day_current_week()
        )
        return this_week_orders

    def yesterday_orders(self):
        yesterday_orders = self.paid_orders.filter(create_time__date=DateVars.last_date)
        return yesterday_orders

    def today_orders(self):
        today_orders = self.paid_orders.filter(create_time__date=DateVars.current_date)
        return today_orders

    def get_peak_business_hours(self, date1=None, date2=None):
        if date1 is None or date2 is None:
            hours = (
                self.paid_orders.filter(create_time__date=DateVars.current_date)
                .annotate(hour=ExtractHour("create_time"))
                .values("hour")
                .annotate(order_count=Count("id"))
            )
        else:
            hours = (
                self.paid_orders.filter(create_time__date__range=(date1, date2))
                .annotate(hour=ExtractHour("create_time"))
                .values("hour")
                .annotate(order_count=Count("id"))
            )

        each_hour = {}
        for hour in hours:
            if each_hour.get(list(hour.values())[0]):
                each_hour[list(hour.values())[0]] += list(hour.values())[1]
            else:
                each_hour[list(hour.values())[0]] = list(hour.values())[1]

        for _ in range(7, 24):
            if not each_hour.get(_):
                each_hour[_] = 0

        return json.dumps(each_hour)

    def get_count_by_status(self, date1=None, date2=None):
        if not date1 and not date2:
            date1 = DateVars.current_date
            date2 = DateVars.current_date

        counts_by_status = Order.objects.filter(
            create_time__date__range=(date1, date2)
        ).aggregate(
            accepted=Count(Case(When(status="a", then=1), output_field=IntegerField())),
            pending=Count(Case(When(status="p", then=1), output_field=IntegerField())),
            rejected=Count(Case(When(status="r", then=1), output_field=IntegerField())),
        )
        accepted = counts_by_status["accepted"]
        pending = counts_by_status["pending"]
        rejected = counts_by_status["rejected"]
        return json.dumps(
            {"accepted": accepted, "pending": pending, "rejected": rejected}
        )

    def get_personnel_count_by_date(self, date1=None, date2=None):
        if date1 is None or date2 is None:
            personnels_count = (
                self.orders.filter(status="a")
                .values("personnel", "personnel__full_name")
                .annotate(personnel_count=Count("id"))
            )
        else:
            personnels_count = (
                self.orders.filter(status="a")
                .filter(create_time__date__range=(date1, date2))
                .values("personnel", "personnel__full_name")
                .annotate(personnel_count=Count("id"))
            )
        return self.get_personnel_count(personnels_count)

    def get_personnel_count(self, personnels_count):
        each_personnel = {}
        for item in personnels_count:
            if item["personnel"] is not None:
                if each_personnel.get(
                    f"{list(item.values())[0]}-{list(item.values())[1]}"
                ):
                    each_personnel[
                        f"{list(item.values())[0]}-{list(item.values())[1]}"
                    ] += list(item.values())[2]
                else:
                    each_personnel[
                        f"{list(item.values())[0]}-{list(item.values())[1]}"
                    ] = list(item.values())[2]
        return json.dumps(each_personnel)

    def orders_with_costs(self, number, orders=None):
        total_price = []
        if not orders:
            orders = self.paid_orders.select_related("customer")
        for order in orders:
            total_price.append(order.get_total_price())
        orders_with_costs = zip(orders[:number], total_price[:number])
        return orders_with_costs

    def total_sales(self):
        return sum(paid_order.get_total_price() for paid_order in self.paid_orders)

    def count_orders(self):
        return self.paid_orders.count()


class BestCustomer:
    def __init__(self) -> None:
        self.orders = (
            Order.objects.select_related("customer")
            .prefetch_related("orderitem_set")
            .all()
        )

    def best_customers_custom(self, number, date1=None, date2=None):
        orders = self.orders.filter(create_time__date__range=(date1, date2))
        best_customers_custom = {}
        return self.add_best_customer(orders, best_customers_custom, number)

    def best_customers_all(self, number):
        orders = self.orders
        best_customers_all = {}
        return self.add_best_customer(orders, best_customers_all, number)

    def best_customers_year(self, number):
        orders = self.orders.filter(create_time__year=DateVars.get_current_year())
        best_customers_year = {}
        return self.add_best_customer(orders, best_customers_year, number)

    def best_customers_month(self, number):
        orders = self.orders.filter(
            create_time__date__gte=DateVars.get_first_day_current_month()
        )
        best_customers_month = {}
        return self.add_best_customer(orders, best_customers_month, number)

    def best_customers_week(self, number):
        orders = self.orders.filter(
            create_time__date__gte=DateVars.get_first_day_current_week()
        )
        best_customers_month = {}
        return self.add_best_customer(orders, best_customers_month, number)

    def add_best_customer(self, orders, best_customers, number):
        for order in orders:
            if best_customers.get(order.customer.phone_number):
                best_customers[order.customer.phone_number] += order.get_total_price()
            else:
                best_customers[order.customer.phone_number] = order.get_total_price()
        return sorted(best_customers.items(), key=lambda x: x[1], reverse=True)[:number]

    def count_customers(self):
        return Customer.objects.count()


class Comparison:
    def get_change_percenatge(self, current, last):
        try:
            result = ((current - last) / last) * 100
        except ZeroDivisionError:
            result = current * 100
        return result

    def return_dictionary(self, current, last):
        return {
            "current": current,
            "last": last,
            "changes_percentage": self.get_change_percenatge(current, last),
            "changes_numebr": current - last,
        }


class ComparisonOrders(Comparison, OrdersManager):
    def __init__(self):
        self.orders = Order.objects.all().order_by("-create_time")
        self.paid_orders = Order.objects.filter(paid=True).order_by("-create_time")

    def compare_order_daily(self):
        last_date_orders_count = self.paid_orders.filter(
            create_time__date=DateVars.last_date
        ).count()
        current_date_orders_count = self.today_orders().count()

        return self.return_dictionary(current_date_orders_count, last_date_orders_count)

    def compare_order_weekly(self):
        last_week_orders_count = self.paid_orders.filter(
            create_time__range=(
                DateVars.get_first_day_last_week(),
                DateVars.get_last_day_last_week(),
            )
        ).count()
        current_week_orders_count = self.this_week_orders().count()

        return self.return_dictionary(current_week_orders_count, last_week_orders_count)

    def compare_order_monthly(self):
        last_month_orders_count = self.paid_orders.filter(
            create_time__range=(
                DateVars.get_first_day_last_month(),
                DateVars.get_last_day_last_month(),
            )
        ).count()
        current_month_orders_count = self.this_month_orders().count()
        return self.return_dictionary(
            current_month_orders_count, last_month_orders_count
        )

    def compare_order_annual(self):
        last_year_orders_count = self.paid_orders.filter(
            create_time__year=DateVars.get_last_year()
        ).count()
        current_year_orders_count = self.this_year_orders().count()
        return self.return_dictionary(current_year_orders_count, last_year_orders_count)


class ComparisonCustomers(Comparison):
    def __init__(self):
        self.customers = Customer.objects.all().order_by("-joined")

    def compare_customer_daily(self):
        current_date_customers_count = self.customers.filter(
            joined__date=DateVars.current_date
        ).count()
        last_date_customers_count = self.customers.filter(
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
                DateVars.get_first_day_current_month(),
                DateVars.current_date,
            )
        ).count()
        return self.return_dictionary(
            current_month_customers_count, last_month_customers_count
        )

    def compare_customer_annual(self):
        last_year_customers_count = self.customers.filter(
            joined__year=DateVars.get_last_year()
        ).count()
        current_year_customers_count = self.customers.filter(
            joined__year=DateVars.get_current_year()
        ).count()
        return self.return_dictionary(
            current_year_customers_count, last_year_customers_count
        )


class MostSellerCategories:
    def most_seller_categories_all(self, number):
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

    def most_seller_categories_custom(self, number, date1=None, date2=None):
        if not date1 and not date2:
            date1 = DateVars.current_date
            date2 = DateVars.current_date

        print(date1)
        print(date2)

        filtered_categories = Category.objects.filter(
            product__orderitem__order__create_time__date__range=(date1, date2)
        )
        print(filtered_categories)
        print(self.count_quantity(filtered_categories, number))
        return self.count_quantity(filtered_categories, number)

    def count_quantity(self, filtered_categories, number):
        categories = filtered_categories.annotate(
            total_quantity=Sum("product__orderitem__quantity")
        ).order_by("-total_quantity")[:number]
        products_dict = self.to_dict(categories)
        products_json = self.to_json(products_dict)
        return products_json

    def to_dict(self, most_sellar):
        category_quantity = {}
        for category in most_sellar:
            category_quantity[category.name] = category.total_quantity
        return category_quantity

    def to_json(self, products_dict):
        return json.dumps(products_dict)


class SalesDashboardVars:
    def __call__(self):
        most_seller: MostSellerProducts = MostSellerProducts(3)
        most_seller_all: dict = most_seller.most_seller_products_all()
        most_seller_year: dict = most_seller.most_seller_products_year()
        most_seller_month: dict = most_seller.most_seller_products_month()
        most_seller_week: dict = most_seller.most_seller_products_week()

        most_seller_morning: dict = most_seller.most_seller_products_morning()
        most_seller_noon: dict = most_seller.most_seller_products_noon()
        most_seller_night: dict = most_seller.most_seller_products_night()

        compare_orders: ComparisonOrders = ComparisonOrders()
        compare_orders_annual: dict = compare_orders.compare_order_annual()
        compare_orders_monthly: dict = compare_orders.compare_order_monthly()
        compare_orders_weekly: dict = compare_orders.compare_order_weekly()
        compare_orders_daily: dict = compare_orders.compare_order_daily()

        compare_customers: ComparisonCustomers = ComparisonCustomers()
        compare_customers_annual: dict = compare_customers.compare_customer_annual()
        compare_customers_monthly: dict = compare_customers.compare_customer_monthly()
        compare_customers_weekly: dict = compare_customers.compare_customer_weekly()
        compare_customers_daily: dict = compare_customers.compare_customer_daily()

        compare_orders_list: List[dict] = [
            compare_orders_annual,
            compare_orders_monthly,
            compare_orders_weekly,
            compare_orders_daily,
        ]

        compare_customers_list: List[dict] = [
            compare_customers_annual,
            compare_customers_monthly,
            compare_customers_weekly,
            compare_customers_daily,
        ]

        most_seller_products_list: List[dict] = [
            most_seller_all,
            most_seller_year,
            most_seller_month,
            most_seller_week,
        ]

        compare_orders_title: List[str] = [
            "Annual Sales",
            "Monthly Sales",
            "Weekly Sales",
            "Daily Sales",
        ]

        compare_customers_title: List[str] = [
            "Annual Customer Changes",
            "Monthly Customer Changes",
            "Weekly Customer Changes",
            "Daily Customer Changes",
        ]

        most_seller_products_title: List[str] = [
            "Top Selling Products of all time",
            "Top Selling Products of the year",
            "Top Selling Products of the month",
            "Top Selling Products of the week",
        ]

        compare_orders_with_titles: Iterable = zip(
            compare_orders_list, compare_orders_title
        )
        compare_customers_with_titles: Iterable = zip(
            compare_customers_list, compare_customers_title
        )
        most_seller_products_with_titles: Iterable = zip(
            most_seller_products_list, most_seller_products_title
        )

        context = {
            "compare_orders_with_titles": compare_orders_with_titles,
            "most_seller_products_with_titles": most_seller_products_with_titles,
            "most_seller_morning": most_seller_morning,
            "most_seller_noon": most_seller_noon,
            "most_seller_night": most_seller_night,
            "compare_customers_with_titles": compare_customers_with_titles,
        }

        return context


class DashboardVars:
    def __call__(self, request):
        orders = OrdersManager()
        orders_with_costs = orders.orders_with_costs(10)
        orders_count = orders.count_orders()
        total_sales = orders.total_sales()
        personnels_count = Personnel.objects.all().count()
        orders_count_by_status = orders.get_count_by_status
        orders_count_by_status = get_date_from_staff(
            request,
            orders_count_by_status,
            "orders_status_date1",
            "orders_status_date2",
        )

        each_hour = orders.get_peak_business_hours
        each_hour = get_date_from_staff(
            request,
            each_hour,
            "peak_bussiness_hours_date1",
            "peak_bussiness_hours_date2",
        )

        each_personnel_count = orders.get_personnel_count_by_date
        each_personnel_count = get_date_from_staff(
            request,
            each_personnel_count,
            "orders_personnel_date1",
            "orders_personnel_date2",
        )

        categories = MostSellerCategories()
        best_categories_all = categories.most_seller_categories_all(5)
        best_categories_year = categories.most_seller_categories_year(5)
        best_categories_month = categories.most_seller_categories_month(5)
        best_categories_week = categories.most_seller_categories_week(5)

        best_categories_custom = categories.most_seller_categories_custom
        best_categories_custom = get_date_from_staff(
            request,
            best_categories_custom,
            "best_categories_date1",
            "best_categories_date2",
            number=5,
        )
        print(best_categories_custom)

        best_customers = BestCustomer()
        best_customers_all = best_customers.best_customers_all(5)
        best_customers_year = best_customers.best_customers_year(5)
        best_customers_month = best_customers.best_customers_month(5)
        best_customers_week = best_customers.best_customers_week(5)

        best_customers_custom = best_customers.best_customers_custom
        best_customers_custom = get_date_from_staff(
            request,
            best_customers_custom,
            "best_customers_date1",
            "best_customers_date2",
            number=5,
        )

        print(best_customers_custom)


        customers_count = best_customers.count_customers()
        best_customers_list = [
            best_customers_all,
            best_customers_year,
            best_customers_month,
            best_customers_week,
        ]
        best_customer_titles = [
            "Best customers of all time",
            "Best customers of all year",
            "Best customers of all month",
            "Best customers of all week",
        ]

        best_customers_with_title = zip(best_customers_list, best_customer_titles)

        general_data_list = [
            total_sales,
            orders_count,
            customers_count,
            personnels_count,
        ]
        general_data_titles = [
            "total sales",
            "orders count",
            "customers count",
            "personnels count",
        ]

        general_data_with_title = zip(general_data_list, general_data_titles)

        context = {
            "best_categories_all": best_categories_all,
            "best_categories_year": best_categories_year,
            "best_categories_month": best_categories_month,
            "best_categories_week": best_categories_week,
            "best_customers_with_title": best_customers_with_title,
            "customers_count": customers_count,
            "orders_count": orders_count,
            "total_sales": total_sales,
            "orders_with_costs": orders_with_costs,
            "each_hour": each_hour,
            "each_personnel_count": each_personnel_count,
            "orders_count_by_status": orders_count_by_status,
            "general_data_with_title": general_data_with_title,
            "best_customers_custom": best_customers_custom,
            "best_categories_custom": best_categories_custom,
        }

        return context
