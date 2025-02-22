from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('register', views.register, name='register'),
    
    
    # Admin Pages
    path('admin_dashboard', views.admin_dashboard, name='admin-dashboard'),
    path('all_request', views.all_requests, name='request'),
        path('PaymentRequest/', views.PaymentRequest, name='PaymentRequest'),
        path('unpaidRequest/', views.unpaidRequest, name='unpaidRequest'),
        path('registerCustomer/', views.registerCustomer, name='registerCustomer'),
        path('customers/', views.customers, name='customers'),
        path('balance/', views.balance, name='balance'),
        path('users/', views.users, name='users'),
        path('birthdays/', views.birthdays, name='birthdays'),
]