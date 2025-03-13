from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.agent_dashboard, name='agent-dashboard'),
    path('agent-payto/', views.payto, name='agent_payto'),
    path('cashIn/', views.cashIn, name='cashIn'),
    path('cashOut/', views.cashOut, name='cashOut'),
    
    path('bank_deposit/', views.agencyBank, name='agencyBank'),
    path('view_bank_deposits/', views.view_bank_deposits, name='view_bank_deposits'),
    path('get-banks/', views.get_banks, name='get_banks'),
    path('get-accounts/', views.get_accounts, name='get_accounts'),
    path('get-customer-details/', views.get_customer_details, name='get_customer_details'),
    
    path('withdrawal/', views.withdrawal, name='withdrawal'),
    path('view_bank_withdrawals/', views.view_bank_withdrawals, name='view_bank_withdrawals'),
    
    # Transaction summaries
    path('TotalTransactionSum/', views.TotalTransactionSum, name='TotalTransactionSum'),
    path('cashin_summary_date/', views.cashin_summary_date, name='cashin_summary_date'),
    path('cashin_summary/<str:date>/', views.cashin_summary, name='cashin_summary'),
    path('cashout_summary_date/', views.cashout_summary_date, name='cashout_summary_date'),
    path('cashout_summary/<str:date>/', views.cashout_summary, name='cashout_summary'),
    path('bank_deposit_summary_date/', views.bank_deposit_summary_date, name='bank_deposit_summary_date'),
    path('bank_deposit_summary/<str:date>/', views.bank_deposit_summary, name='bank_deposit_summary'),
    path('bank_withdrawal_summary_date/', views.bank_withdrawal_summary_date, name='bank_withdrawal_summary_date'),
    path('bank_withdrawal_summary/<str:date>/', views.bank_withdrawal_summary, name='bank_withdrawal_summary'),
    path('cash_summary_date/', views.cash_summary_date, name='cash_summary_date'),
    path('cash_summary/<str:date>/', views.cash_summary, name='cash_summary'),
    path('payment_summary_date/', views.payment_summary_date, name='payment_summary_date'),
    path('payment_summary/<str:date>/', views.payment_summary, name='payment_summary'),
    path('agent-commission/', views.commission, name='agent-commission'),
    
    
    
    path('PaymentSummary/', views.PaymentSummary, name='PaymentSummary'),
    
    path('customerReg/', views.customerReg, name='customerReg'),
    path('accountReg/', views.accountReg, name='accountReg'),
    path('my-customers/', views.my_customers, name='my_customers'),
    path('my-customer-detail/<int:customer_id>/accounts/', views.my_customer_detail, name='my_customer_detail'),
    
    
    path('payment/', views.payment, name='payment'),
    path('view_payment/', views.view_payments, name='view_payments'),
    
    path('cashFloatRequest/', views.cashFloatRequest, name='cashFloatRequest'),
    
    path('customer-care/', views.customer_care, name='customer_care'),
    path('customer-complains/', views.customer_complains, name='customer_complains'),
    path('view-customer-complains/', views.view_customer_complains, name='view_customer_complains'),
    path('hold_account/', views.customer_hold_account, name='customer_hold_account'),
    path('view_hold_account/', views.view_customer_hold_account, name='view_customer_hold_account'),
    path('customer-fraud/', views.customer_fraud, name='customer_fraud'),
    path('view-customer-fraud/', views.view_customer_fraud, name='view_customer_fraud'),
    
    path('calculate/', views.calculate, name='calculate'),
    path('view_calculate/', views.view_calculator, name='view_calculator'),

    path('efloat_account/', views.open_e_float_account, name='open_efloat_account'),
    path('view_efloat_account/', views.view_e_float_account, name='view_efloat_account'),
    
    # Notifications
    path('cashin_notifications/', views.cashin_notifications, name='cashin_notifications'),
    path('cashout_notifications/', views.cashout_notifications, name='cashout_notifications'),
    path('bank_deposit_notifications/', views.bank_deposit_notifications, name='bank_deposit_notifications'),
    path('bank_withdrawal_notifications/', views.bank_withdrawal_notifications, name='bank_withdrawal_notifications'),
    path('cash_notifications/', views.cash_notifications, name='cash_notifications'),
    path('payment_notifications/', views.payment_notifications, name='payment_notifications'),
    path('payto_notifications/', views.payto_notifications, name='payto_notifications'),
    path('errorPage/', views.errorPage, name='errorPage'),
]
