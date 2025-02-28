from django.urls import path
from . import views

urlpatterns = [
    path('owner-dashboard/', views.owner_dashboard, name='owner-dashboard'),
    
    path('registerAgent/', views.registerAgent, name='registerAgent'),
    path('myAgent/', views.myAgent, name='myAgent'),

    path('report/', views.report, name='report'),
    path('payto/', views.payto, name='payto'),
    path('pay_to_mechant/', views.pay_to_mechant, name='pay_to_mechant'),
    path('pay_to_agent_detail/', views.pay_to_agent_detail, name='pay_to_agent_detail'),
    path('pay_to_mechant_detail/', views.pay_to_mechant_detail, name='pay_to_mechant_detail'),
    path('users/', views.users, name='users'),
    path('register_customer/', views.register_customer, name='register_customer'),
    path('flot_resources/', views.flot_resources, name='flot_resources'),
    path('agent_accounts/', views.agent_accounts, name='agent_accounts'),
    path('bank_account/', views.bank_account, name='bank_account'),
    path('bank_linkage/', views.bank_linkage, name='bank_linkage'),
    path('customer_care/', views.customer_care, name='customer_care'),
    
    # Financial requests
    path('bank_deposit_requests/', views.bank_deposit_requests, name='bank_deposit_requests'),
    path('owner/approve_bank_deposit/<int:deposit_id>/', views.approve_bank_deposit, name='approve_bank_deposit'),
    path('owner/reject_bank_deposit/<int:deposit_id>/', views.reject_bank_deposit, name='reject_bank_deposit'),
    
    path('bank_withdrawal_requests/', views.bank_withdrawal_requests, name='bank_withdrawal_requests'),
    path('owner/approve_bank_withdrawal/<int:withdrawal_id>/', views.approve_bank_withdrawal, name='approve_bank_withdrawal'),
    path('owner/reject_bank_withdrawal/<int:withdrawal_id>/', views.reject_bank_withdrawal, name='reject_bank_withdrawal'),
    
    path('agentDetail/<int:agent_id>/', views.agentDetail, name='agentDetail'),
    path('agentCustomer/', views.agentCustomer, name='agentCustomer'),
    path('bankDeposit/', views.bankDeposit, name='bankDeposit'),
    path('bank_withdrawal/', views.bank_withdrawal, name='bank_withdrawal'),
    path('bank_with_detail/', views.bank_with_detail, name='bank_with_detail'),
    path('bankDepositDetail/', views.bankDepositDetail, name='bankDepositDetail'),
    
    path('cash_In/', views.cash_In, name='cash_In'),
    path('cash_out_agent/', views.cash_out_agent, name='cash_out_agent'),
    path('cash_in_detail/', views.cash_in_detail, name='cash_in_detail'),
    path('cash_out_detail/', views.cash_out_detail, name='cash_out_detail'),
    path('pay_to/', views.pay_to, name='pay_to'),
    path('all_transaction/', views.all_transaction, name='all_transaction'),
    path('complains/', views.complains, name='complains'),
    path('fraud/', views.fraud, name='fraud'),
    path('hold-account/', views.hold_account, name='hold_account'),

]