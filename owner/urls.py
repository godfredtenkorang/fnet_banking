from django.urls import path
from . import views

urlpatterns = [
    path('owner-dashboard/', views.owner_dashboard, name='owner-dashboard'),
    path('owner-account/', views.owner_account, name='owner-account'),
    path('owner-account-update/', views.update_owner_balances, name='update-account'),
    
    path('registerAgent/', views.registerAgent, name='registerAgent'),
    path('myAgent/', views.myAgent, name='myAgent'),
    
    path('account/<int:branch_id>/', views.get_all_agents, name='get_all_agents'),
    path('get_owner/view_agent_e_float_drawer/<int:agent_id>/', views.view_agent_e_float_drawer, name='view_agent_e_float_drawer'),
    path('get_owner/add_capital_to_drawer/<int:agent_id>/', views.add_capital_to_drawer, name='add_capital_to_drawer'),

    path('customers/', views.customers, name='all_agent_customers'),
    path('customers_account_details/<int:customer_id>/', views.customers_account_details, name='customers_account_details'),
    path('update_customer/<int:customer_id>/update/', views.update_customer, name='update_customer'),
    
    path('cash_requests/', views.cash_requests, name='cash_requests'),
    path('ecash_requests/', views.e_cash_requests, name='ecash_requests'),
    path('branch_bank_requests/', views.branch_bank_requests, name='branch_bank_requests'),
    path('owner/<int:request_id>/approve_request/', views.approve_cash_and_ecash_request, name='approve_cash_and_ecash_request'),
    path('owner/<int:request_id>/reject_request/', views.reject_cash_and_ecash_request, name='reject_cash_and_ecash_request'),
    
    path('view_pending_payment_requests/', views.view_payment_requests, name='view_payment_requests'),
    path('approve_branch_payment/<int:payment_id>/', views.approve_payment, name='approve_payment'),
    path('reject_branch_payment/<int:payment_id>/', views.reject_payment, name='reject_payment'),
    
    path('pay_to_agent_detail/', views.pay_to_agent_detail, name='pay_to_agent_detail'),
    path('pay_to_mechant_detail/', views.pay_to_mechant_detail, name='pay_to_mechant_detail'),
    path('users/', views.users, name='users'),
    path('register_customer/', views.register_customer, name='register_customer'),
    path('flot_resources/', views.flot_resources, name='flot_resources'),
    path('agent_accounts/', views.agent_accounts, name='agent_accounts'),
    path('bank_account/', views.bank_account, name='bank_account'),
    path('bank_linkage/', views.bank_linkage, name='bank_linkage'),
    
    # Financial requests
    path('bank_deposit_requests/', views.bank_deposit_requests, name='bank_deposit_requests'),
    path('owner/approve_bank_deposit/<int:deposit_id>/', views.approve_bank_deposit, name='approve_bank_deposit'),
    path('owner/reject_bank_deposit/<int:deposit_id>/', views.reject_bank_deposit, name='reject_bank_deposit'),
    
    path('bank_withdrawal_requests/', views.bank_withdrawal_requests, name='bank_withdrawal_requests'),
    path('owner/approve_bank_withdrawal/<int:withdrawal_id>/', views.approve_bank_withdrawal, name='approve_bank_withdrawal'),
    path('owner/reject_bank_withdrawal/<int:withdrawal_id>/', views.reject_bank_withdrawal, name='reject_bank_withdrawal'),
    # Branches
    path('agentDetail/<int:agent_id>/', views.agentDetail, name='agentDetail'),
    path('agentCustomer/<int:branch_id>/', views.agentCustomer, name='agentCustomer'),
    path('bankDeposit/<int:branch_id>/', views.bankDeposit, name='bankDeposit'),
    path('bankDepositDetail/<int:branch_id>/<str:date>/', views.bankDepositDetail, name='bankDepositDetail'),
    path('delete_branch_bank_deposit/<int:deposit_id>/', views.delete_agent_bank_deposit, name='delete_branch_bank_deposit'),
    
    path('bank_withdrawal/<int:branch_id>/', views.bank_withdrawal, name='bank_withdrawal'),
    path('bank_with_detail/<int:branch_id>/<str:date>/', views.bank_with_detail, name='bank_with_detail'),
    path('delete_branch_bank_withdrawal/<int:withdrawal_id>/', views.delete_agent_bank_withdrawal, name='delete_branch_bank_withdrawal'),
    
    path('cash_in/<int:branch_id>/', views.cash_In, name='cash_In'),
    path('cash_in_detail/<int:branch_id>/<str:date>/', views.cash_in_detail, name='cash_in_detail'),
    path('delete_branch_cashin/<int:cash_id>/', views.delete_agent_cash_ins, name='delete_branch_cashin'),
    
    path('cash_out_agent/<int:branch_id>/', views.cash_out_agent, name='cash_out_agent'),
    path('cash_out_detail/<int:branch_id>/<str:date>/', views.cash_out_detail, name='cash_out_detail'),
    path('delete_branch_cashout/<int:cash_id>/', views.delete_agent_cash_outs, name='delete_branch_cashout'),
    
    
    path('branch_bank_deposit_date/<int:branch_id>/', views.branch_bank_deposit_date, name='branch_bank_deposit_date'),
    path('branch_bank_deposit_transaction/<int:branch_id>/<str:date>/', views.branch_bank_deposit_transaction, name='branch_bank_deposit_transaction'),
    path('delete_agent_bank_deposit/<int:deposit_id>/', views.delete_agent_bank_deposit, name='delete_agent_bank_deposit'),
    
    path('branch_bank_withdrawal_transactions_date/<int:branch_id>/', views.branch_bank_withdrawal_transactions_date, name='branch_bank_withdrawal_transactions_date'),
    path('branch_bank_withdrawal_transactions/<int:branch_id>/<str:date>/', views.branch_bank_withdrawal_transactions, name='branch_bank_withdrawal_transactions'),
    path('delete_branch_bank_withdrawal/<int:deposit_id>/', views.delete_branch_bank_withdrawal, name='delete_branch_bank_withdrawal'),
    
    
    path('branch_ecash_transactions_date/<int:branch_id>/', views.branch_ecash_transactions_date, name='branch_ecash_transactions_date'),
    path('branch_ecash_transactions/<int:branch_id>/<str:date>/', views.branch_ecash_transactions, name='branch_ecash_transactions'),
    path('delete_branch_ecash/<int:ecash_id>/', views.delete_branch_ecash, name='delete_branch_ecash'),
    
    path('branch_payment_transactions_date/<int:branch_id>/', views.branch_payment_transactions_date, name='branch_payment_transactions_date'),
    path('branch_payment_transactions/<int:branch_id>/<str:date>/', views.branch_payment_transactions, name='branch_payment_transactions'),
    path('delete_branch_payment/<int:payment_id>/', views.delete_branch_payment, name='delete_branch_payment'),
    
    
    path('pay_to/', views.pay_to, name='pay_to'),
    path('all_transaction/', views.all_transaction, name='all_transaction'),
    path('commission/', views.commission, name='commission'),
    path('branch_balance/<int:branch_id>/', views.branch_balance, name='branch_balance'),
    path('branch_reports/<int:branch_id>/', views.branch_report_view, name='branch_report_view'),
    
    path('customer_care_view/', views.customer_care, name='my_customer_care'),
    path('complains/', views.complains, name='all_complains'),
    path('fraud/', views.fraud, name='all_fraud'),
    path('hold-account/', views.hold_account, name='all_hold_account'),
    
    
    # Mobilization Registration
    # path('register_mobilization/', views.register_mobilization, name='register_mobilization'),
    path('register_mobilization/', views.registerMobilization, name='register_mobilization'),
    path('my_mobilizations/', views.myMobilization, name='my_mobilizations'),
    
    # Mobilization Approvals
    path('mobilization_bank_deposit_requests/', views.mobilization_bank_deposit_requests, name='mobilization_bank_deposit_requests'),
    path('approve_mobilization_bank_deposit/<int:deposit_id>/', views.approve_mobilization_bank_deposit, name='approve_mobilization_bank_deposit'),
    path('reject_mobilization_bank_deposit/<int:deposit_id>/', views.reject_mobilization_bank_deposit, name='reject_mobilization_bank_deposit'),
    
    path('mobilization_bank_withdrawal_requests/', views.mobilization_bank_withdrawal_requests, name='mobilization_bank_withdrawal_requests'),
    path('approve_mobilization_bank_withdrawal/<int:withdrawal_id>/', views.approve_mobilization_withdrawal, name='approve_mobilization_withdrawal'),
    path('reject_mobilization_bank_withdrwal/<int:withdrawal_id>/', views.reject_mobilization_withdrawal, name='reject_mobilization_withdrawal'),
    
    path('mobilization_payment_requests/', views.mobilization_payment_requests, name='mobilization_payment_requests'),
    path('approve_mobilization_payment/<int:payment_id>/', views.approve_mobilization_payment, name='approve_mobilization_payment'),
    path('reject_mobilization_payment/<int:payment_id>/', views.reject_mobilization_payment, name='reject_mobilization_payment'),
    
    # Mobilization Details
    
    path('mobilization_customers/<int:mobilization_id>/', views.mobilization_customers, name='mobilization_customers'),
    path('delete_customer/<int:mobilization_id>/delete/', views.delete_mobilization_customer, name='delete_mobilization_customer'),
    
    
    path('mobilization_detail/<int:mobilization_id>/', views.mobilization_agent_detail, name='mobilization_agent_detail'),
    path('mobilization_bank_deposit_transactions_date/<int:mobilization_id>/', views.mobilization_bank_deposit_transactions_date, name='mobilization_bank_deposit_transactions_date'),
    path('mobilization_bank_deposit_transactions/<int:mobilization_id>/<str:date>/', views.mobilization_bank_deposit_transactions, name='mobilization_bank_deposit_transactions'),
    path('update_mobilization_bank_deposit/<int:deposit_id>/', views.update_mobilization_bank_deposit, name='update_mobilization_bank_deposit'),
    path('delete_mobilization_bank_deposit/<int:deposit_id>/', views.delete_mobilization_bank_deposit, name='delete_mobilization_bank_deposit'),
    
    path('mobilization_bank_withdrawal_transactions_date/<int:mobilization_id>/', views.mobilization_bank_withdrawal_transactions_date, name='mobilization_bank_withdrawal_transactions_date'),
    path('mobilization_bank_withdrawal_transactions/<int:mobilization_id>/<str:date>/', views.mobilization_bank_withdrawal_transactions, name='mobilization_bank_withdrawal_transactions'),
    path('delete_mobilization_bank_withdrawal/<int:withdrawal_id>/', views.delete_mobilization_bank_withdrawal, name='delete_mobilization_bank_withdrawal'),
    
    path('mobilization_payment_transactions_date/<int:mobilization_id>/', views.mobilization_payment_transactions_date, name='mobilization_payment_transactions_date'),
    path('mobilization_payment_transactions/<int:mobilization_id>/<str:date>/', views.mobilization_payment_transactions, name='mobilization_payment_transactions'),
    path('update_mobilization_payment/<int:payment_id>/', views.update_mobilization_payment, name='update_mobilization_payment'),
    path('delete_mobilization_payment/<int:payment_id>/', views.delete_mobilization_payment, name='delete_mobilization_payment'),

    path('mobilization_all_transactions/', views.mobilization_all_transactions, name='mobilization_all_transactions'),
    
    path('mobilization_account_detail/<int:mobilization_id>/', views.mobilization_account_detail, name='mobilization_account_detail'),
    # path('add_mobilization_account/<int:mobilization_id>/', views.add_mobilization_account, name='add_mobilization_account'),
    
    path('mobilization_reports/<int:mobilization_id>/', views.mobilization_report_view, name='mobilization_report_view'),
    
    
    path('delete_message/', views.delete_transaction_notification, name='delete_transaction_notification'),
    
    
    
]