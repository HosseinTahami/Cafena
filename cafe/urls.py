# django imports
from django.urls import path

# inner modules imports
# from .views import SearchView, HomeView, ProductDetailView
from .views import HomeView, ProductDetailView

app_name = "cafe"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    # path("search_results/", SearchView.as_view(), name="search_results"),
    path("product_detail/<int:pk>", ProductDetailView.as_view(), name="product_detail"),
]
