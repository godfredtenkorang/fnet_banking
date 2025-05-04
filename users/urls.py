from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView

urlpatterns = [
    path('', views.login_user, name='login'),
    path('logout/', views.logout, name='logout'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    
    path('send-otp/', views.send_reset_otp, name='send_reset_otp'),
    path('verify-otp/', views.verify_reset_otp, name='verify_reset_otp'),
    path('change-password/', views.change_password, name='change_password'),
    
    path('register/', views.register, name='register'),
    path('verify_registration_otp/', views.verify_registration_otp, name='verify_registration_otp'),
    path('approve_user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('unapprove_user/<int:user_id>/', views.unapprove_user, name='unapprove_user'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    
    
    # Admin Pages
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('all_request/', views.all_requests, name='request'),
    path('PaymentRequest/', views.PaymentRequest, name='PaymentRequest'),
    path('unpaidRequest/', views.unpaidRequest, name='unpaidRequest'),
    path('register_owner/', views.register_owner, name='register_owner'),
    path('my_owners/', views.my_owners, name='my_owners'),
    path('balance/', views.balance, name='balance'),
    path('users/', views.all_users, name='all_users'),
    path('birthdays/', views.birthdays, name='birthdays'),
    
    
    path('register-driver/', views.register_driver, name='register-driver'),
    path('my-drivers/', views.my_drivers, name='my_drivers'),
    path('my-driver/<int:driver_id>/', views.driver_detail, name='driver_detail'),
    
    
    # API
     path('login/', LoginView.as_view(), name='user_login'),
     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     
    
]