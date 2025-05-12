from django.urls import path
from products import views

urlpatterns = [
    path('api/recommendations/', views.get_recommendations, name='recommendations'),
    path('api/browsing-history/', views.save_browsing_history, name='save_browsing_history'),
    path('api/recommendation-click/', views.log_recommendation_click, name='log_recommendation_click'),
    path('api/products', views.get_products, name='get_products'),
    path('api/get-csrf-token', views.get_csrf_token, name='get_csrf_token'), 
]