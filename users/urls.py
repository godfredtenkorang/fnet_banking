from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('register', views.register, name='register'),
    
    
    # Admin Pages
    path('admin_dashboard', views.admin_dashboard, name='admin-dashboard'),
    path('all_request', views.all_requests, name='request')
]