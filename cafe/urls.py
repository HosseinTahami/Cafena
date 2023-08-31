# django imports
from django.urls import path

# inner modules imports
from .views import HomeView, ProductDetailView , AboutView ,ContactView

app_name = "cafe"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("product_detail/<int:pk>", ProductDetailView.as_view(), name="product_detail"),
    path("about/" , AboutView.as_view() , name='about'),
    path("contact/" , ContactView.as_view() , name='contact'),
]
