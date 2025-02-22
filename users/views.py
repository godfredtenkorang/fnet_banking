from django.shortcuts import render

# Create your views here.
def admin_dashboard(request):
    return render(request, 'users/admin_dashboard/dashboard.html')

def all_requests(request):
    return render(request, 'users/admin_dashboard/request.html')

def register(request):
    return render(request, 'users/register.html')

def login(request):
    return render(request, 'users/login.html')

def PaymentRequest(request):
    return render(request, 'users/admin_dashboard/PaymentRequest.html')

def unpaidRequest(request):
    return render(request, 'users/admin_dashboard/unpaidRequest.html')

def registerCustomer(request):
    return render(request, 'users/admin_dashboard/registerCustomer.html')

def customers(request):
    return render(request, 'users/admin_dashboard/customers.html')

def balance(request):
    return render(request, 'users/admin_dashboard/balance.html')

def users(request):
    return render(request, 'users/admin_dashboard/users.html')

def birthdays(request):
    return render(request, 'users/admin_dashboard/birthdays.html')