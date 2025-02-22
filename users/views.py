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