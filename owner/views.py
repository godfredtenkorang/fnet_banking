from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required, user_passes_test
from users.forms import AgentRegistrationForm
from users.models import Agent, Owner
from banking.models import EFloatAccount
from banking.forms import AddCapitalForm
from agent.models import BankDeposit, BankWithdrawal, CashAndECashRequest, PaymentRequest
from django.contrib import messages
from decimal import Decimal
from django.utils import timezone


# Check if the user is an Owner
def is_owner(user):
    return user.role == 'OWNER'

@login_required
@user_passes_test(is_owner)
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

def is_owner(user):
    return user.role == 'OWNER'

@login_required
@user_passes_test(is_owner)
def cash_requests(request):
    pending_requests = CashAndECashRequest.objects.filter(float_type='Cash' ,status='Pending').order_by('-created_at')
    context = {
        'pending_requests': pending_requests,
        'title': 'Cash Requests'
    }
    return render(request, 'owner/pay_to/cash_requests.html', context)

def e_cash_requests(request):
    pending_requests = CashAndECashRequest.objects.filter(status='Pending').order_by('-created_at')
    context = {
        'pending_requests': pending_requests,
        'title': 'Cash Requests'
    }
    return render(request, 'owner/pay_to/ecash_requests.html', context)


@login_required
@user_passes_test(is_owner)
def approve_cash_and_ecash_request(request, request_id):
    request_obj = get_object_or_404(CashAndECashRequest, id=request_id)
    
    if request.method == 'POST':
        approved_amount = request.POST.get('approved_amount')
        try:
            approved_amount = Decimal(approved_amount)
            if approved_amount < 0 or approved_amount > request_obj.amount:
                messages.error(request, 'Invalid approved amount')
                return redirect('cash_requests')
            
            # Calculate the remaining amount (arrears)
            remaining_amount = request_obj.amount - approved_amount
            request_obj.arrears = remaining_amount
            
            # If there are arrears, keep the status as Pending
            if remaining_amount > 0:
                request_obj.status = 'Pending'
                messages.success(request, f'Partial approval successful. Approved Amount: GH¢{approved_amount}, Remaining Amount: GH¢{remaining_amount}')
            
            else:
                # If no arrears, mark the request as Approved
                request_obj.status = 'Approved'
                messages.success(request, 'Request fully approved.')
            # Save the request status and arrears
            request_obj.save()
            return redirect('cash_requests')
        except ValueError:
            messages.success(request, 'Invalid input for approved amount.')
            return redirect('cash_requests')
    context = {
        'request_obj': request_obj,
        'title': 'Approve Request'
    }
    return render(request, 'owner/pay_to/approve_cash_and_ecash_request.html', context)

@login_required
@user_passes_test(is_owner)
def reject_cash_and_ecash_request(request, request_id):
    request_obj = get_object_or_404(CashAndECashRequest, id=request_id)
    request_obj.status = 'Rejected'
    request_obj.save()
    messages.success(request, 'Request rejected.')
    return redirect('cash_requests')

@login_required
@user_passes_test(is_owner)
def get_all_agents(request):
    agents = Agent.objects.all()
    context = {
        'agents': agents,
        'title': 'View Agents'
    }
    return render(request, 'owner/float_account/account.html', context)

@login_required
@user_passes_test(is_owner)
def view_agent_e_float_drawer(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    today = timezone.now().date()
    account = get_object_or_404(EFloatAccount, agent=agent, date=today)
    context = {
        'account': account,
        'agent': agent,
        'title': 'View Agent EFloat'
    }
    return render(request, 'owner/float_account/account_detail.html', context)


@login_required
@user_passes_test(is_owner)
def add_capital_to_drawer(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    today = timezone.now().date()
    account = get_object_or_404(EFloatAccount, agent=agent, date=today)
    
    if request.method == 'POST':
        form = AddCapitalForm(request.POST)
        if form.is_valid():
            additional_capital = form.cleaned_data['additional_capital']
            if account.add_capital(additional_capital):
                messages.success(request, f'Successfully added GH¢{additional_capital} to the capital.')
            else:
                messages.error(request, 'Invalid capital amount.')
            return redirect('view_agent_e_float_drawer', agent_id=agent.id)
    else:
        form = AddCapitalForm()
    context = {
        'form': form,
        'agent': agent,
        'title': 'Add Capital'
    }
    return render(request, 'owner/float_account/add_capital_account.html', context)


@login_required
@user_passes_test(is_owner)
def view_payment_requests(request):
    
    payments = PaymentRequest.objects.filter(status='Pending').order_by('-created_at')
    
    context = {
        'payments': payments,
        'title': 'Payment Requests'
    }
    return render(request, 'owner/payments/pending_payments.html', context)

@login_required
@user_passes_test(is_owner)
def approve_payment(request, payment_id):
    payment = get_object_or_404(PaymentRequest, id=payment_id)
    payment.status = 'Approved'
    payment.save()
    messages.success(request, 'Payment request approved successfully.')
    return redirect('view_payment_requests')

@login_required
@user_passes_test(is_owner)
def reject_payment(request, payment_id):
    payment = get_object_or_404(PaymentRequest, id=payment_id)
    payment.status = 'Rejected'
    payment.save()
    messages.success(request, 'Payment request rejected.')
    return redirect('view_payment_requests')
                

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

# @login_required
# @user_passes_test(is_owner)
def complains(request):
    return render(request, 'owner/customerCare/complains.html')  

def fraud(request):
    return render(request, 'owner/customerCare/fraud.html')  

def hold_account(request):
    return render(request, 'owner/customerCare/holdAccount.html')  
