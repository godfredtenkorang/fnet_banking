from django.shortcuts import render

# Create your views here.
def agent_dashboard(request):
    return render(request, 'agent/dashboard.html')