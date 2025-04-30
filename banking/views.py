from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from banking.models import CustomerAccount


def customerSupport(request):
    return render(request, 'banking/customerSupport.html')

def custom_404_view(request, exception):
    context = {
        'title': '404'
    }
    return render(request, 'banking/404.html', status=404, context=context)


def get_banks(request):
    phone_number = request.GET.get('phone_number')
    customers = CustomerAccount.objects.filter(phone_number=phone_number).values('bank').distinct()
    banks = [customer['bank'] for customer in customers]
    return JsonResponse(banks, safe=False)

def get_accounts(request):
    phone_number = request.GET.get('phone_number')
    bank = request.GET.get('bank')
    customers = CustomerAccount.objects.filter(phone_number=phone_number, bank=bank).values('account_number')
    accounts = [customer['account_number'] for customer in customers]
    return JsonResponse(accounts, safe=False)

def get_customer_details(request):
    account_number = request.GET.get('account_number')
    customer = get_object_or_404(CustomerAccount, account_number=account_number)
    data = {
        'account_name': customer.account_name
    }
    return JsonResponse(data)
    