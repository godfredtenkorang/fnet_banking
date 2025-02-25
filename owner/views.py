from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from users.forms import AgentRegistrationForm
from users.models import Agent, Owner


def owner_dashboard(request):
    return render(request, 'owner/dashboard.html')

def registerAgent(request):
    if request.method == 'POST':
        form = AgentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registerAgent')
    else:
        form = AgentRegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'owner/registerAgent.html', context)

def myAgent(request):
    my_agents = Agent.objects.all()
    context = {
        'my_agents': my_agents,
        'title': 'My Agents',
    }
    return render(request, 'owner/myAgent.html', context)

# def get_owner(request):
#     users = Owner.objects.filter(user=request.user)
#     return {'users': users}

def report(request):
    return render(request, 'owner/report.html')


def payto(request):
    return render(request, 'owner/payto.html')

def users(request):
    return render(request, 'owner/users.html')

def register_customer(request):
    return render(request, 'owner/register_customer.html')

def flot_resources(request):
    return render(request, 'owner/flot_resources.html')

def agent_accounts(request):
    return render(request, 'owner/agent_accounts.html')

def bank_account(request):
    return render(request, 'owner/bank_account.html')

def bank_linkage(request):
    return render(request, 'owner/bank_linkage.html')

def customer_care(request):
    return render(request, 'owner/customer_care.html')


def financial_services(request):
    return render(request, 'owner/FinancialServices.html')

def agentDetail(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    context = {
        'agent': agent
    }
    return render(request, 'owner/agent_Detail/agentDetail.html', context)

def agentCustomer(request):
    return render(request, 'owner/agent_Detail/agentCustomer.html')

def bankDeposit(request):
    return render(request, 'owner/agent_Detail/bankDeposit.html')

def bankDepositDetail(request):
    return render(request, 'owner/agent_Detail/bankDepositDetail.html')

def bank_with_detail(request):
    return render(request, 'owner/agent_Detail/bank_with_detail.html')

def bank_withdrawal(request):
    return render(request, 'owner/agent_Detail/bank_withdrawal.html')

def cash_In(request):
    return render(request, 'owner/agent_Detail/cash_In.html')

def cash_in_detail(request):
    return render(request, 'owner/agent_Detail/cash_in_detail.html')  

def cash_out_detail(request):
    return render(request, 'owner/agent_Detail/cash_out_detail.html')  

def cash_out_agent(request):
    return render(request, 'owner/agent_Detail/cash_out_agent.html')  

def pay_to(request):
    return render(request, 'owner/agent_Detail/pay_to.html')  

def all_transaction(request):
    return render(request, 'owner/agent_Detail/all_transaction.html')  
