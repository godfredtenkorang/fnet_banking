from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_dashboard, name='customer-dashboard')
]