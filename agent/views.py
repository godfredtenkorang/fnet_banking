from django.shortcuts import render

# Create your views here.
def agent_dashboard(request):
    return render(request, 'agent/dashboard.html')

def cashIn(request):
    return render(request, 'agent/cashIn.html')

def cashOut(request):
    return render(request, 'agent/cashOut.html')


def agencyBank(request):
    return render(request, 'agent/agencyBank.html')

def withdrawal(request):
    return render(request, 'agent/withdrawal.html')

def TotalTransactionSum(request):
    return render(request, 'agent/TotalTransactionSum.html')