# django imports
from django.urls import path

# inner modules imports
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("verify_personnel/", views.UserVerifyView.as_view(), name="verify_personnel"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path(
        "sales_dashboard/", views.SalesDashboardView.as_view(), name="sales_dashboard"
    ),
    path(
        "messages_dashboard/", views.MessagesDashboardView.as_view(), name="messages_dashboard"
    ),
    path(
        "orders_dashboard/", views.OrdersDashboardView.as_view(), name="orders_dashboard"
    ),
    path("order_detail/<int:pk>", views.OrderDetailView.as_view(), name="order_detail"),
]
