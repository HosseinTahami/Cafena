from django.test import TestCase
from django.urls import reverse ,resolve
from orders.views import AddOrderView  ,CartView , CartAddView ,CartRemoveView ,OrderAccept ,OrderReject , CheckoutView


class TestordersUrls(TestCase):        
    def test_AddOrderView(self):
        url=reverse('orders:add_order' )
        self.assertEqual(resolve(url).func.view_class,AddOrderView)

    # def test_OrderDetailView(self):
    #     url=reverse('orders:order_detail' )
    #     self.assertEqual(resolve(url).func.view_class,OrderDetailView)

    def test_CartView(self):
        url=reverse('orders:cart' )
        self.assertEqual(resolve(url).func.view_class,CartView)
        

    def test_CartAddView(self):
        url=reverse('orders:cart_add' , args=('1',))
        self.assertEqual(resolve(url).func.view_class,CartAddView)

    def test_CartRemoveView(self):
        url=reverse('orders:cart_remove' , args=('2',))
        self.assertEqual(resolve(url).func.view_class,CartRemoveView)

    def test_OrderAccept(self):
        url=reverse('orders:order_accept' , args=('5',))
        self.assertEqual(resolve(url).func.view_class,OrderAccept)


    def test_OrderReject(self):
        url=reverse('orders:order_reject' , args=('5',))
        self.assertEqual(resolve(url).func.view_class,OrderReject)



    def test_CheckoutView(self):
        url=reverse('orders:checkout' )
        self.assertEqual(resolve(url).func.view_class,CheckoutView)