from django.urls import path
from products import views

urlpatterns = [
    path('recommend/', views.RecommendProductsView.as_view(), name='recommend_products'),
]