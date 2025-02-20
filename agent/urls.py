from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.agent_dashboard, name='agent-dashboard'),
    path('cashIn', views.cashIn, name='cashIn'),
    path('cashOut', views.cashOut, name='cashOut'),
     path('agencyBank', views.agencyBank, name='agencyBank'),
     path('withdrawal', views.withdrawal, name='withdrawal'),
     path('TotalTransactionSum', views.TotalTransactionSum, name='TotalTransactionSum'),
]