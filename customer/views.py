from django.shortcuts import render

# Create your views here.
def customer_dashboard(request):
    return render(request, 'customer/dashboard.html')