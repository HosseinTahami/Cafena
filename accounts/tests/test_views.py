from django.test import TestCase , Client ,RequestFactory
from django.urls import reverse 
from accounts.models import  Customer, Personnel
from orders.models import Order, OrderItem, Product ,  Table
from accounts.views import DashboardView ,ShowAllOrders
from model_bakery   import baker


class UserLoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_user_login_GET(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/personnel_login.html")
        

    def test_user_login_POST_valid(self):
        response = self.client.post(reverse("accounts:login"), data={"phone_number": "1234567890"})
        self.assertRedirects(response, reverse("accounts:verify_personnel"))

    def test_user_login_POST_invalid(self):
        response = self.client.post(reverse("accounts:login"), data={"phone_number": "0000"})
        self.assertEqual(response.status_code, 302)
        

class UserVerifyViewTest(TestCase):
    def setUp(self):
        self.client = Client()


    def test_user_verify_POST_valid(self):
        session = self.client.session
        session["personnel_verify"] = {"phone_number": "1234567890", "code": "1234"}
        session.save()


    def test_user_verify_POST_invalid(self):
        session = self.client.session
        session["personnel_verify"] = {"phone_number": "1234567890", "code": "1234"}






#class 4
class OrderModelTest(TestCase):
    def setUp(self):
        self.order = baker.make(Order ,status='p')
        self.product1 = baker.make(Product ,name='Product 1', price=10)
        self.product2 = baker.make(Product ,name='Product 2', price=20)
        self.orderitem1 = baker.make(OrderItem ,quantity=2, price=self.product1.price, order=self.order, product=self.product1)
        self.orderitem2 = baker.make(OrderItem ,quantity=1, price=self.product2.price, order=self.order, product=self.product2)

    def test_get_total_price(self):
        expected_total_price = self.orderitem1.get_cost() * self.orderitem1.quantity + self.orderitem2.get_cost() * self.orderitem2.quantity
        self.assertEqual(self.order.get_total_price(), expected_total_price)


#class5
class DashboardViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_dashboard_view(self):
        request = self.factory.get('/dashboard/')
        response = DashboardView.as_view()(request)
        self.assertEqual(response.status_code, 200)


#class6
class OrderModelTest(TestCase):
    def setUp(self):
        self.order = baker.make(Order,status='p')
        self.product1 = baker.make(Product ,name='Product 1', price=10)
        self.product2 = baker.make(Product ,name='Product 2', price=20)
        self.orderitem1 = baker.make(OrderItem ,quantity=2, price=self.product1.price, order=self.order, product=self.product1)
        self.orderitem2 = baker.make(OrderItem ,quantity=1, price=self.product2.price, order=self.order, product=self.product2)

    def test_get_total_price(self):
        expected_total_price = self.orderitem1.get_cost() * self.orderitem1.quantity + self.orderitem2.get_cost() * self.orderitem2.quantity



#class7
class OrderDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(name='Test Customer')
        self.personnel = Personnel.objects.create(full_name='Test Personnel')
        self.table = baker.make(Table,table_number=1)
        self.order = baker.make(Order ,status='p', customer=self.customer, personnel=self.personnel, table=self.table)

    def test_order_detail_view(self):
        response = self.client.get(reverse("accounts:order_detail", args=[self.order.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/order_detail.html')



#class8
class ShowAllOrdersTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_show_all_orders_view(self):
        request = self.factory.get('/all_orders/')
        response = ShowAllOrders.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('orders_with_costs', response.context_data)
        