from django.urls import path
from products import views

urlpatterns = [
    path('api/recommendations/', views.get_recommendations, name='recommendations'),
    path('api/browsing-history/', views.save_browsing_history, name='save_browsing_history'),
]