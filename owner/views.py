from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required, user_passes_test
from users.forms import AgentRegistrationForm
from users.models import Agent, Owner
from banking.models import EFloatAccount
from agent.models import BankDeposit, BankWithdrawal
from django.contrib import messages


# Check if the user is an Owner
def is_owner(user):
    return user.is_authenticated and user.is_owner


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
    return render(request, 'owner/pay_to/payto.html')

def pay_to_mechant(request):
    return render(request, 'owner/pay_to/pay_to_mechant.html')

def pay_to_agent_detail(request):
    return render(request, 'owner/pay_to/pay_to_agent_detail.html')

def pay_to_mechant_detail(request):
    return render(request, 'owner/pay_to/pay_to_mechant_detail.html')

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


@login_required
def approve_bank_deposit(request, deposit_id):
    deposit = get_object_or_404(BankDeposit, id=deposit_id)
    account = deposit.agent.e_float_drawers.filter(date=deposit.date_deposited).first()
    
    if not account:
        messages.error(request, 'No e-float account found for this date')
        return redirect('bank_deposit_requests')
    
    # Check if the bank has sufficient balance
    bank_balance = getattr(account, f"{deposit.bank.lower()}_balance")
    if deposit.amount > bank_balance:
        messages.error(request, f'Insufficient balance is {deposit.bank}')
        return redirect('bank_deposit_requests')
    
    # Update the status and drawer balance
    deposit.status = 'Approved'
    deposit.save()
    account.update_balance_for_bank_deposit(deposit.bank, deposit.amount, deposit.status)
    messages.success(request, 'Bank Deposit approved succussfully')
    return redirect('bank_deposit_requests')

@login_required
def reject_bank_deposit(request, deposit_id):
    deposit = get_object_or_404(BankDeposit, id=deposit_id)
    deposit.status = 'Rejected'
    deposit.save()
    messages.success(request, 'Bank Deposit rejected')
    return redirect('bank_deposit_requests')




@login_required
def bank_deposit_requests(request):
    pending_deposits = BankDeposit.objects.filter(status='Pending').order_by('-date_deposited', '-time_deposited')
    context = {
        'pending_deposits': pending_deposits,
        'title': 'Bank Deposit Requests'
    }
    return render(request, 'owner/financial_services/bank_deposit.html', context)


@login_required
def approve_bank_withdrawal(request, withdrawal_id):
    withdrawal = get_object_or_404(BankWithdrawal, id=withdrawal_id)
    account = withdrawal.agent.e_float_drawers.filter(date=withdrawal.date_withdrawn).first()
    
    if not account:
        messages.error(request, 'No e-float account found for this date')
        return redirect('bank_withdrawal_requests')
    
    # Check if the bank has sufficient balance
    bank_balance = getattr(account, f"{withdrawal.bank.lower()}_balance")
    if withdrawal.amount > bank_balance:
        messages.error(request, f'Insufficient balance is {withdrawal.bank}')
        return redirect('bank_withdrawal_requests')
    
    # Update the status and drawer balance
    withdrawal.status = 'Approved'
    withdrawal.save()
    account.update_balance_for_bank_withdrawal(withdrawal.bank, withdrawal.amount, withdrawal.status)
    messages.success(request, 'Bank Withdrawal approved succussfully')
    return redirect('bank_withdrawal_requests')

@login_required
def reject_bank_withdrawal(request, withdrawal_id):
    withdrawal = get_object_or_404(BankWithdrawal, id=withdrawal_id)
    withdrawal.status = 'Rejected'
    withdrawal.save()
    messages.success(request, 'Bank Withdrawal rejected')
    return redirect('bank_withdrawal_requests')

@login_required
def bank_withdrawal_requests(request):
    pending_withdrawals = BankWithdrawal.objects.filter(status='Pending').order_by('-date_withdrawn', '-time_withdrawn')
    context = {
        'pending_withdrawals': pending_withdrawals,
        'title': 'Bank Withdrawal Requests'
    }
    return render(request, 'owner/financial_services/bank_withdrawal.html', context)

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

def complains(request):
    return render(request, 'owner/customerCare/complains.html')  

def fraud(request):
    return render(request, 'owner/customerCare/fraud.html')  

def hold_account(request):
    return render(request, 'owner/customerCare/holdAccount.html')  
