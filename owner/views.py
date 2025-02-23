from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


def owner_dashboard(request):
    return render(request, 'owner/dashboard.html')

def registerAgent(request):
    return render(request, 'owner/registerAgent.html')

def myAgent(request):
    return render(request, 'owner/myAgent.html')

def report(request):
    return render(request, 'owner/report.html')


def payto(request):
    return render(request, 'owner/payto.html')

def users(request):
    return render(request, 'owner/users.html')

def register_customer(request):
    return render(request, 'owner/register_customer.html')

def flot_resources(request):
    return render(request, 'owner/flot_resources.html')

def agent_accounts(request):
    return render(request, 'owner/agent_accounts.html')

def bank_account(request):
    return render(request, 'owner/bank_account.html')

def bank_linkage(request):
    return render(request, 'owner/bank_linkage.html')

def customer_care(request):
    return render(request, 'owner/customer_care.html')


def financial_services(request):
    return render(request, 'owner/FinancialServices.html')