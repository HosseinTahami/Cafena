# django imports
from typing import Any
from django import http
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# inner modules imports
from utils import send_otp_code
from orders.models import Order, OrderItem
from .utils_dashboard import OrdersManager, SalesDashboardVars, DashboardVars
from .forms import UserCustomerLoginForm, OTPForm, OrderItemForm


# third party imports
from random import randint
import datetime
import pytz


# Create your views here.
class UserLoginView(View):
    form_class = UserCustomerLoginForm
    template_name = "accounts/personnel_login.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("cafe:home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        session = request.session["personnel_verify"] = {}
        if form.is_valid():
            current_datetime = datetime.datetime.now(tz=pytz.timezone("Asia/Tehran"))
            request.session["my_datetime"] = current_datetime.isoformat()
            cd = form.cleaned_data
            phone_number = cd["phone_number"]
            code = randint(1000, 9999)
            if Personnel.objects.filter(phone_number=phone_number).exists():
                # send_otp_code(phone_number, code)
                print(code)
            session["phone_number"] = phone_number
            session["code"] = code
            session["created_at"] = current_datetime.isoformat()

            return redirect("accounts:verify_personnel")

        return render(request, self.template_name, {"form": form})


class UserVerifyView(View):
    form_class = OTPForm

    def setup(self, request, *args, **kwargs):
        self.session = request.session["personnel_verify"]
        return super().setup(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        context = {"form": form}
        return render(request, "accounts/personnel_verify.html", context=context)

    def post(self, request):
        form = self.form_class(request.POST)
        phone_number = self.session["phone_number"]
        if form.is_valid():
            cd = form.cleaned_data
            digit1 = cd["digit1"]
            digit2 = cd["digit2"]
            digit3 = cd["digit3"]
            digit4 = cd["digit4"]
            entered_code = int(digit1 + digit2 + digit3 + digit4)

            user = authenticate(
                request,
                phone_number=phone_number,
                entered_code=entered_code,
            )
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in Successfully", "success")
                return redirect("accounts:dashboard")
            else:
                messages.error(request, "The code or phone_number is wrong!", "error")
                return redirect("accounts:verify_personnel")


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("cafe:home")


class ManageOrders(View):
    def get(self, request):
        orders = Order.objects.all()
        total_price = []
        for order in orders:
            total_price.append(order.get_total_price())
        orders_with_costs = zip(orders, total_price)
        # context = {'orders': orders, "total_price": total_price}
        context = {"orders_with_costs": orders_with_costs}
        return render(request, "accounts/manage_orders.html", context=context)


class DashboardView(View):
    def get(self, request):
        context_instance = DashboardVars()
        context = context_instance(request)
        return render(request, "accounts/dashboard.html", context=context)


class SalesDashboardView(View):
    def get(self, request):
        context_instance = SalesDashboardVars()
        context = context_instance(request)
        return render(request, "accounts/sales_dashboard.html", context=context)


class OrderDetailView(View):
    form_class = OrderItemForm

    def setup(self, request, *args, **kwargs):
        print(*args)
        print(*kwargs)
        self.order = Order.objects.get(pk=kwargs["pk"])
        return super().setup(request, *args, **kwargs)

    def get(self, request, pk):
        form = self.form_class()
        total_price = self.order.get_total_price()
        context = {"order": self.order, "total_price": total_price, "form": form}
        return render(
            request,
            "accounts/order_detail.html",
            context=context,
        )

    def post(self, request, pk):
        form = self.form_class(request.POST)
        print(form)
        if form.is_valid():
            cd = form.cleaned_data
            print(cd)
            if OrderItem.objects.filter(order=self.order,product=cd["product"]).exists():
                orderitem = OrderItem.objects.get(order=self.order,product=cd["product"])
                orderitem.quantity += cd["quantity"]
                orderitem.save()
            else:
                new_orderitem = form.save(commit=False)
                new_orderitem.order = self.order
                new_orderitem.price = new_orderitem.product.price
                new_orderitem.save()

        return redirect("accounts:order_detail", pk)

class ShowAllOrders(TemplateView):
    template_name = "accounts/all_orders_table.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders_manager = OrdersManager()
        orders_with_costs = orders_manager.orders_with_costs(None)
        context["orders_with_costs"] = orders_with_costs
        return context
