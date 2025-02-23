from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_user, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('approve_user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('unapprove_user/<int:user_id>/', views.unapprove_user, name='unapprove_user'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),
    
    
    # Admin Pages
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('all_request/', views.all_requests, name='request'),
    path('PaymentRequest/', views.PaymentRequest, name='PaymentRequest'),
    path('unpaidRequest/', views.unpaidRequest, name='unpaidRequest'),
    path('registerCustomer/', views.registerCustomer, name='registerCustomer'),
    path('customers/', views.customers, name='customers'),
    path('balance/', views.balance, name='balance'),
    path('users/', views.users, name='users'),
    path('birthdays/', views.birthdays, name='birthdays'),
]