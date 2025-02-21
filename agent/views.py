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

def PaymentSummary(request):
    return render(request, 'agent/PaymentSummary.html')

def customerReg(request):
    return render(request, 'agent/customerReg.html')

def accountReg(request):
    return render(request, 'agent/accountReg.html')

def payment(request):
    return render(request, 'agent/payment.html')

def cashFloatRequest(request):
    return render(request, 'agent/cashFloatRequest.html')

def calculate(request):
    return render(request, 'agent/calculate.html')