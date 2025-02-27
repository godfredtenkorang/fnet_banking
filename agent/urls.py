from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.agent_dashboard, name='agent-dashboard'),
    path('cashIn/', views.cashIn, name='cashIn'),
    path('cashOut/', views.cashOut, name='cashOut'),
    path('agencyBank/', views.agencyBank, name='agencyBank'),
    path('withdrawal/', views.withdrawal, name='withdrawal'),
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
