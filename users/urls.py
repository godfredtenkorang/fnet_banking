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
    
    path('all_customers/', views.customers, name='all-customers'),
    path('get_customer/<int:customer_id>/detail', views.my_customer_detail, name='get_customer_detail'),
    
    path('add-customer-accounts/', views.customer_accounts, name='all-customer-accounts'),
    path('delete-customer-account/<int:account_id>/', views.delete_account, name='delete-customer-account'),
    
    # Accountant
    path('register_accountant/', views.register_accountant, name='register-accountant'),
    path('reports/monthly/', views.my_accountants, name='monthly_report'),
    path('all_transactions/', views.all_transactions, name='all_transactions'),
    
    path('transaction/<int:accountant_id>/', views.accountant_detail, name='accountant_detail'),
    
    
    # API
     path('login/', LoginView.as_view(), name='user_login'),
     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     
    path('export-customer-accounts-pdf/', views.export_customer_accounts_pdf, name='export_customer_accounts_pdf'),
    
    # export
    path('export_users/', views.export_users, name='export_users'),
    path('export_branches/', views.export_branches, name='export_branches'),
    path('export_owners/', views.export_owners, name='export_owners'),
    path('export-agents/', views.export_agents, name='export_agents'),
    path('export-mobilizations/', views.export_mobilizations, name='export_mobilizations'),
    path('export-drivers/', views.export_drivers, name='export_drivers'),
    path('export-customers/', views.export_customers, name='export_customers'),
    # Mobilization
    path('export-mobilization-bank-deposits/', views.export_bank_deposits, name='export_bank_deposits'),
    path('export-mobilization-payment-requests/', views.export_payment_requests, name='export_payment_requests'),
    
    
    # Agent
    path('export-agent-bank-deposits/', views.export_agent_bank_deposits, name='export_agent_bank_deposits'),
    path('export-cash-ecash-requests/', views.export_cash_ecash_requests, name='export_cash_ecash_requests'),
    path('export-agent-payment-requests/', views.export_agent_payment_requests, name='export_agent_payment_requests'),
    
    
    
    
    # import
    path('import_users/', views.import_users, name='import_users'),
    path('import_branches/', views.import_branches, name='import_branches'),
    path('import_owners/', views.import_owners, name='import_owners'),
    path('import-agents/', views.import_agents, name='import_agents'),
    path('import-mobilizations/', views.import_mobilizations, name='import_mobilizations'),
    path('import-drivers/', views.import_drivers, name='import_drivers'),
    path('import-customers/', views.import_customers, name='import_customers'),
    
    # Mobilization
    path('import-mobilization-bank-deposits/', views.import_bank_deposits, name='import_bank_deposits'),
    path('import-mobilization-payment-requests/', views.import_payment_requests, name='import_payment_requests'),
    
    # Agent
    path('import-agent-bank-deposits/', views.import_agent_bank_deposits, name='import_agent_bank_deposits'),
    path('import-cash-ecash-requests/', views.import_cash_ecash_requests, name='import_cash_ecash_requests'),
    path('import-agent-payment-requests/', views.import_agent_payment_requests, name='import_agent_payment_requests'),
    
    # backups
    path('all_backups/', views.all_backups, name='all_backups'),
    
    # backup pages
    path('user_import/', views.user_import_export, name='user_import'),
    path('branch_import/', views.branch_import_export, name='branch_import'),
    path('owners_page/', views.owner_import_export, name='owners_import'),
    path('agents_page/', views.agent_import_export, name='agents_import'),
    path('mobilizations_page/', views.mobilization_import_export, name='mobilizations_import'),
    path('drivers_page/', views.driver_import_export, name='drivers_import'),
    path('customers_page/', views.customer_import_export, name='customers_import'),
    
    path('mobilization_bank_deposit_page/', views.mobilization_bank_deposit_import_export, name='mobilization_bank_deposits_import'),
    path('mobilization_payment_request_page/', views.mobilization_payment_request_import_export, name='mobilization_payment_requests_import'),
    
    path('agent_bank_deposit_page/', views.agent_bank_deposit_import_export, name='agent_bank_deposits_import'),
    path('agent_cash_ecash_page/', views.agent_cash_ecash_import_export, name='agent_cash_ecash_requests_import'),
    path('agent_payment_request_page/', views.agent_payment_request_import_export, name='agent_payment_requests_import'),
]