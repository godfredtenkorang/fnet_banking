from django.shortcuts import render


def customerSupport(request):
    return render(request, 'banking/customerSupport.html')