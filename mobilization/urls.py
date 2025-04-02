from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='mobilization_dashboard'),
    # path('add_mobilization_account/', views.open_mobilization_account, name='add_mobilization_account'),
    path('mobilization_account/', views.mobilization_account, name='mobilization_account'),
    path('mobilization_payto/', views.payto, name='mobilization_payto'),
    
    path('get-banks/', views.get_banks, name='get_banks'),
    path('get-accounts/', views.get_accounts, name='get_accounts'),
    path('get-customer-details/', views.get_customer_details, name='get_customer_details'),
    # path('mobilization_banks/', views.get_banks, name='mobilization_banks'),
    # path('mobilization_accounts/', views.get_accounts, name='mobilization_accounts'),
    # path('mobilization_customers/', views.get_customer_details, name='mobilization_customers'),
    path('mobilization_bank_deposit/', views.bank_deposit, name='mobilization_bank_deposit'),
    path('get_bank_deposit/', views.get_bank_deposit, name='get_bank_deposit'),
    path('get_bank_withdrawal/', views.get_bank_withdrawal, name='get_bank_withdrawal'),
    path('get_payments/', views.get_payments, name='get_payments'),
    
    path('mobilization_bank_withdrawal/', views.bank_withdrawal, name='mobilization_bank_withdrawal'),
    path('mobilization_payment/', views.payment, name='mobilization_payment'),
    path('mobilization_customer_registration/', views.customer_registration, name='mobilization_customer_registration'),
    path('mobilization_account_registration/', views.customer_account_registration, name='customer_account_registration'),
    path('mobilization_all_customers/', views.my_customers, name='mobilization_all_customers'),
    path('mobilization_all_customers/<int:customer_id>/accounts/', views.my_customer_detail, name='mobilization_customer_detail'),
    path('mobilization_customer_detail/<int:customer_id>/', views.update_customer_details, name='update_customer_details'),
    path('mobilization_transaction_summary/', views.transaction_summary, name='mobilization_transaction_summary'),
    path('mobilization_deposit_summary_date/', views.bank_deposit_summary_date, name='mobilization_deposit_summary_date'),
    path('mobilization_deposit_summary/<str:date>/', views.bank_deposit_summary, name='mobilization_deposit_summary'),
    path('screenshot_bank_deposit/<int:deposit_id>/', views.screenshot_bank_deposit, name='screenshot_bank_deposit'),
    path('mobilization_withdrawal_summary_date/', views.bank_withdrawal_summary_date, name='mobilization_withdrawal_summary_date'),
    path('mobilization_withdrawal_summary/<str:date>/', views.bank_withdrawal_summary, name='mobilization_withdrawal_summary'),
    path('mobilization_payment_summary_date/', views.payment_summary_date, name='mobilization_payment_summary_date'),
    path('mobilization_payment_summary/<str:date>/', views.payment_summary, name='mobilization_payment_summary'),
    
    path('mobilization_calculator/', views.calculator, name='mobilization_calculator'),
    path('view_mobilization_calculator/', views.view_calculator, name='view_mobilization_calculator'),
    
    
    # Notifications
    
    path('mobilization_bank_deposit_success/', views.bank_deposit_notifications, name='mobilization_bank_deposit_success'),
    path('mobilization_bank_withdrawal_success/', views.bank_withdrawal_notifications, name='mobilization_bank_withdrawal_success'),
    path('mobilization_payment_success/', views.payment_notifications, name='mobilization_payment_success'),
    path('mobilization_payto_success/', views.payto_notifications, name='mobilization_payto_success'),
    
    path('mobilization_report/', views.report, name='mobilization_report'),
    path('mobilization_report_view/', views.view_report, name='mobilization_report_view'),
]