from django.urls import path
from products import views

urlpatterns = [
    path('recommend/', views.RecommendProductsView.as_view(), name='recommend_products'),
    path('history/', views.BrowsingHistoryView.as_view(), name='browsing_history'),
    path('view-product/', views.ViewProduct.as_view(), name='view_product'),
]