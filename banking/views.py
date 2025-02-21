from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'banking/index.html')

def dashboard(request):
    return render(request, 'banking/dashboard.html')

def signUp(request):
    return render(request, 'banking/signUp.html')

def customerSupport(request):
    return render(request, 'banking/customerSupport.html')