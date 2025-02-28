from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.agent_dashboard, name='agent-dashboard'),
    path('cashIn/', views.cashIn, name='cashIn'),
    path('cashOut/', views.cashOut, name='cashOut'),
    
    path('bank_deposit/', views.agencyBank, name='agencyBank'),
    path('view_bank_deposits/', views.view_bank_deposits, name='view_bank_deposits'),
    path('get-banks/', views.get_banks, name='get_banks'),
    path('get-accounts/', views.get_accounts, name='get_accounts'),
    path('get-customer-details/', views.get_customer_details, name='get_customer_details'),
    
    path('withdrawal/', views.withdrawal, name='withdrawal'),
    path('view_bank_withdrawals/', views.view_bank_withdrawals, name='view_bank_withdrawals'),
    
    path('TotalTransactionSum/', views.TotalTransactionSum, name='TotalTransactionSum'),
    path('PaymentSummary/', views.PaymentSummary, name='PaymentSummary'),
    path('customerReg/', views.customerReg, name='customerReg'),
    path('accountReg/', views.accountReg, name='accountReg'),
    path('payment/', views.payment, name='payment'),
    path('cashFloatRequest/', views.cashFloatRequest, name='cashFloatRequest'),
    path('calculate/', views.calculate, name='calculate'),

    path('efloat_account/', views.open_e_float_account, name='open_efloat_account'),
    path('view_efloat_account/', views.view_e_float_account, name='view_efloat_account'),
]
