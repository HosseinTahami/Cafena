# django imports
from typing import Any
from django import http
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# inner modules imports
from utils import send_otp_code
from dynamic.models import Dashboard
from orders.models import Order, OrderItem
from cafe.models import Contact
from .utils_dashboard import SalesDashboardVars, DashboardVars, OrdersDashboardVars
from .forms import UserCustomerLoginForm, OTPForm, OrderItemForm
from .models import Personnel

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
                messages.success(
                    request,
                    f"{request.user.full_name}\n Logged In Successfully",
                    "success",
                )
                return redirect("accounts:dashboard")
            else:
                messages.error(
                    request,
                    "The OTP or Phone Number is wrong please check again.",
                    "error",
                )
                return redirect("accounts:verify_personnel")


class UserLogoutView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(
                request, "Logged Out Failed:\n You're not Logged In", "danger"
            )
            return redirect("accounts:login")
        else:
            messages.success(
                request,
                f"{request.user.full_name}\n Logged Out Successfully",
                "warning",
            )
            logout(request)
        return redirect("cafe:home")


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        context_instance = DashboardVars()
        context = context_instance(request)
        # dynamic data
        page_data = Dashboard.get_page_date("Dashboard_Page")
        context["page_data"] = page_data
        return render(request, "accounts/dashboard.html", context=context)


class SalesDashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    required_group = "manager"

    def test_func(self):
        return self.request.user.groups.filter(name=self.required_group).exists()

    def handle_no_permission(self):
        return redirect("accounts:dashboard")

    def get(self, request):
        context_instance = SalesDashboardVars()
        context = context_instance(request)
        # dynamic data
        page_data = Dashboard.get_page_date("Dashboard_Page")
        context["page_data"] = page_data
        return render(request, "accounts/sales_dashboard.html", context=context)


class OrdersDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/all_orders_table.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context_instance = OrdersDashboardVars()
        orders_with_costs_custom = context_instance(self.request)
        context["orders_with_costs_custom"] = orders_with_costs_custom
        page_data = Dashboard.get_page_date("Dashboard_Page")
        context["page_data"] = page_data

        return context

class MessagesDashboardView(LoginRequiredMixin, UserPassesTestMixin, View):
    required_group = "manager"

    def test_func(self):
        return self.request.user.groups.filter(name=self.required_group).exists()

    def handle_no_permission(self):
        return redirect("accounts:dashboard")

    def get(self, request):
        contacts = Contact.objects.all()
        # dynamic data
        page_data = Dashboard.get_page_date("Dashboard_Page")
        context = {"page_data": page_data, "contacts": contacts}
        
        return render(request, "accounts/messages_dashboard.html", context=context)



class OrderDetailView(LoginRequiredMixin, View):
    form_class = OrderItemForm

    def setup(self, request, *args, **kwargs):
        self.order = Order.objects.get(pk=kwargs["pk"])
        return super().setup(request, *args, **kwargs)

    def get(self, request, **kwargs):
        form = self.form_class()
        total_price = self.order.get_total_price()
        page_data = Dashboard.get_page_date("Dashboard_Page")
        context = {"order": self.order, "total_price": total_price, "form": form, "page_data": page_data}
        return render(
            request,
            "accounts/order_detail.html",
            context=context,
        )

    def post(self, request, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if OrderItem.objects.filter(
                order=self.order, product=cd["product"]
            ).exists():
                orderitem = OrderItem.objects.get(
                    order=self.order, product=cd["product"]
                )
                orderitem.quantity += cd["quantity"]
                orderitem.save()
            else:
                new_orderitem = form.save(commit=False)
                new_orderitem.order = self.order
                new_orderitem.price = new_orderitem.product.price
                new_orderitem.save()

        return redirect("accounts:order_detail", kwargs["pk"])
