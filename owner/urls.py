from django.urls import path
from . import views

urlpatterns = [
 path('registerAgent/', views.registerAgent, name='registerAgent'),
 path('myAgent/', views.myAgent, name='myAgent'),

 path('report/', views.report, name='report'),
path('payto/', views.payto, name='payto'),
    path('users/', views.users, name='users'),
    path('register_customer/', views.register_customer, name='register_customer'),
    path('flot_resources/', views.flot_resources, name='flot_resources'),
    path('agent_accounts/', views.agent_accounts, name='agent_accounts'),
    path('bank_account/', views.bank_account, name='bank_account'),
    path('bank_linkage/', views.bank_linkage, name='bank_linkage'),
    path('customer_care/', views.customer_care, name='customer_care'),
        path('financial-services/', views.financial_services, name='financial_services'),

]