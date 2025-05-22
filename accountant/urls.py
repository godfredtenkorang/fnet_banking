from django.urls import path
from . import views

urlpatterns = [

    path('accountant-dashboard/', views.accountant_dashboard, name='accountant_dashboard'),
]