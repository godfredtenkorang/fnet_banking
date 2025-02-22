from django.shortcuts import render

# Create your views here.

def registerAgent(request):
    return render(request, 'owner/registerAgent.html')

def myAgent(request):
    return render(request, 'owner/myAgent.html')