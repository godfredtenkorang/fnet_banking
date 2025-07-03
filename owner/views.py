from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from users.forms import AgentRegistrationForm, MobilizationRegistrationForm, CustomerUpdateForm, DriverRegistrationForm
from users.models import Agent, Owner, Driver
from banking.models import EFloatAccount, MobilizationAccount
from banking.forms import AddCapitalForm, MobilizationAccountForm
from agent.models import BankDeposit, BankWithdrawal, CashAndECashRequest, PaymentRequest, CustomerComplain, HoldCustomerAccount, CustomerFraud, CashInCommission, CashOutCommission, BranchReport, CustomerCashIn, CustomerCashOut
from django.contrib import messages
from decimal import Decimal
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum
from users.models import User, Branch, Mobilization, Customer
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from mobilization.models import BankDeposit as bank_deposits
from mobilization.models import BankWithdrawal as bank_withdrawals
from mobilization.models import PaymentRequest as payment_requests
from mobilization.models import Report as mobilization_reports
from .forms import BankDepositForm, PaymentForm, OwnerBalanceForm
from .models import OwnerBalance
from driver.models import MileageRecord, FuelRecord, Expense
from django.db.models import F


# Check if the user is an Owner
def is_owner(user):
    return user.role == 'OWNER'

@login_required

def owner_account(request):
    
    owner = request.user.owner

    owner_balance = get_object_or_404(OwnerBalance, user=owner)
    
    
    
    branches = Agent.objects.all()
    
    branch_data = []
    
    for branch in branches:
         # Calculate total cash_and_ecash requests (approved only)
        cash_ecash_total = CashAndECashRequest.objects.filter(
            agent=branch,
            status='Approved'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate total payment requests (approved only)
        payment_total = PaymentRequest.objects.filter(
            agent=branch,
            status='Approved'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate balance
        balance = payment_total - cash_ecash_total
        
        branch_data.append({
            'agent': branch,
            'cash_ecash_total': cash_ecash_total,
            'payment_total': payment_total,
            'balance': balance,
        })
        
    mobilizations = Mobilization.objects.all()
    
    mobilization_data = []
    
    for mobilization in mobilizations:
         # Calculate total cash_and_ecash requests (approved only)
        bank_deposits_total = bank_deposits.objects.filter(
            mobilization=mobilization,
            status='Approved'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate total payment requests (approved only)
        payment_requests_total = payment_requests.objects.filter(
            mobilization=mobilization,
            status='Approved'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate balance
        balance = payment_requests_total - bank_deposits_total
        
        mobilization_data.append({
            'mobilization': mobilization,
            'bank_deposits_total': bank_deposits_total,
            'payment_requests_total': payment_requests_total,
            'balance': balance,
        })
        
    

    
    # today = timezone.now().date()
    # ecash_mtn_total = CashAndECashRequest.objects.filter(network='Mtn', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # ecash_telecel_total = CashAndECashRequest.objects.filter(network='Telecel', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # ecash_airteltigo_total = CashAndECashRequest.objects.filter(network='Airtel Tigo', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # ecash_ecobank_total = CashAndECashRequest.objects.filter(bank='Ecobank', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # ecash_fidelity_total = CashAndECashRequest.objects.filter(bank='Fidelity', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # ecash_calbank_total = CashAndECashRequest.objects.filter(bank='Calbank', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # ecash_gtbank_total = CashAndECashRequest.objects.filter(bank='GTbank', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # ecash_accessbank_total = CashAndECashRequest.objects.filter(bank='Access bank', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # cash_total = CashAndECashRequest.objects.filter(cash='Cash', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # payment_mtn_total = PaymentRequest.objects.filter(network='Mtn', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # payment_telecel_total = PaymentRequest.objects.filter(network='Telecel', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # payment_airteltigo_total = PaymentRequest.objects.filter(network='Airtel Tigo', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # payment_ecobank_total = PaymentRequest.objects.filter(bank='Ecobank', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # payment_accessbank_total = PaymentRequest.objects.filter(bank='Access_Bank', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # payment_fidelity_total = PaymentRequest.objects.filter(bank='Fidelity', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # payment_calbank_total = PaymentRequest.objects.filter(bank='Calbank', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    # payment_gtbank_total = PaymentRequest.objects.filter(bank='GTbank', status='Approved', created_at=today).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # mtn_total = ecash_mtn_total + payment_mtn_total
    # telecel_total = ecash_telecel_total + payment_telecel_total
    # airteltigo_total = ecash_airteltigo_total + payment_airteltigo_total
    # ecobank_total = ecash_ecobank_total + payment_ecobank_total
    # accessbank_total = ecash_accessbank_total + payment_accessbank_total
    # fidelity_total = ecash_fidelity_total + payment_fidelity_total
    # calbank_total = ecash_calbank_total + payment_calbank_total
    # gtbank_total = ecash_gtbank_total + payment_gtbank_total
    
    # grand_total = mtn_total + telecel_total + airteltigo_total + ecobank_total + accessbank_total + fidelity_total + calbank_total + gtbank_total
    
    context = {
        # 'mtn_total': mtn_total,
        # 'telecel_total': telecel_total,
        # 'airteltigo_total': airteltigo_total,
        # 'ecobank_total': ecobank_total,
        # 'fidelity_total': fidelity_total,
        # 'calbank_total': calbank_total,
        # 'gtbank_total': gtbank_total,
        # 'accessbank_total': accessbank_total,
        # 'cash_total': cash_total,
        # 'grand_total': grand_total,
        'branch_data': branch_data,
        'mobilization_data': mobilization_data,
        'owner_balance': owner_balance
    }
    return render(request, 'owner/account/owner_account.html', context)

@login_required

def update_owner_balances(request):
    owner = request.user.owner
    owner_balance = OwnerBalance.objects.filter(user=owner).first()
    
    
    if request.method == 'POST':
        form = OwnerBalanceForm(request.POST, instance=owner_balance)
        if form.is_valid():
            form.save()
            return redirect('owner-account')
    else:
        form = OwnerBalanceForm(instance=owner_balance)
    return render(request, 'owner/account/update_balances.html', {'form': form})

def unapproved_users_count(request):
    unapproved_cash_count = CashAndECashRequest.objects.filter(status='Pending', float_type__in=['Cash','Telco'],).count()
    unapproved_payment_count = PaymentRequest.objects.filter(status='Pending').count()
    unapproved_bank_requests_count = CashAndECashRequest.objects.filter(status='Pending', float_type='Bank').count()
    
    pending_deposits_count = bank_deposits.objects.filter(status='Pending').count()
    # pending_withdrawals_count = bank_withdrawals.objects.filter(status='Pending').count()
    payments_count = payment_requests.objects.filter(status='Pending').count()
    
    mobilization_count = pending_deposits_count  + payments_count
    
    context = {
        'unapproved_cash_count': unapproved_cash_count,
        'unapproved_payment_count': unapproved_payment_count,
        'mobilization_count': mobilization_count,
        'unapproved_bank_requests_count': unapproved_bank_requests_count
    }
    return context

# Check if the user is an Owner
def is_owner(user):
    return user.role == 'OWNER'

@login_required
@user_passes_test(is_owner)
def owner_dashboard(request):
    pending_requests = CashAndECashRequest.objects.filter(status='Pending', float_type__in=['Cash','Telco']).order_by('-created_at')
    pending_bank_requests = CashAndECashRequest.objects.filter(status='Pending', float_type__in=['Bank']).order_by('-created_at')
    payments = PaymentRequest.objects.filter(status='Pending').order_by('-created_at')
    
    pending_deposits = bank_deposits.objects.filter(status='Pending').order_by('-date_deposited', '-time_deposited')
    mobilization_payments = payment_requests.objects.filter(status='Pending').order_by('-created_at')
    
    current_month = timezone.now().month
    current_year = timezone.now().year
   
    
     # Get driver's mileage with calculated mileage
    mileage_records = MileageRecord.objects.filter(
        date__month=current_month,
        date__year=current_year
    ).annotate(
        calculated_mileage=F('end_mileage') - F('start_mileage')
    )
    monthly_mileage = mileage_records.aggregate(
        total=Sum('calculated_mileage')
    )['total'] or 0
    
    # Get driver's fuel records for the current month
    fuel_records = FuelRecord.objects.filter(
        date__month=current_month,
        date__year=current_year
    )
    monthly_fuel = fuel_records.aggregate(total=Sum('amount'))['total'] or 0
    
    # Get driver's expenses for the current month
    expenses = Expense.objects.filter(
        date__month=current_month,
        date__year=current_year
    )
    monthly_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    
    context = {
        'pending_requests': pending_requests,
        'pending_bank_requests': pending_bank_requests,
        'payments': payments,
        'pending_deposits': pending_deposits,
        'mobilization_payments': mobilization_payments,
        
        'fuel_records': fuel_records,
        'monthly_fuel': monthly_fuel,
        'monthly_expenses': monthly_expenses,
    }
    return render(request, 'owner/dashboard.html', context)

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





def registerMobilization(request):
    if request.method == 'POST':
        form = MobilizationRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('register_mobilization')
    else:
        form = MobilizationRegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'owner/mobilization/register_mobilization.html', context)

def myMobilization(request):
    mobilizations = Mobilization.objects.all()
    context = {
        'mobilizations': mobilizations,
        'title': 'My Mobilizations',
    }
    return render(request, 'owner/mobilization/my_mobilizations.html', context)

# def get_owner(request):
#     users = Owner.objects.filter(user=request.user)
#     return {'users': users}

def customers(request):
    customers = Customer.objects.all()
    context = {
        'customers': customers,
        'title': 'Customers'
    }
    return render(request, 'owner/customers.html', context)

def customers_account_details(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    mobilization_accounts = customer.customeraccounts.all()
    agent_accounts  = customer.accounts.all()
    context = {
        'customer': customer,
        'agent_accounts': agent_accounts,
        'mobilization_accounts': mobilization_accounts,
        'title': 'Customer Account Details'
    }
    return render(request, 'owner/customers_account_detail.html', context)

def update_customer(request, customer_id):
    customer = Customer.objects.get(id=customer_id)
    if request.method == 'POST':
        form = CustomerUpdateForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            updated_customer = form.save(commit=False)
            updated_customer.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('all_agent_customers')
    else:
        form = CustomerUpdateForm(instance=customer)
        
    context = {
        'form': form,
        'title': 'Update Customer'
    }
        
    return render(request, 'owner/mobilization/customer_update.html', context)

def is_owner(user):
    return user.role == 'OWNER'

@login_required
@user_passes_test(is_owner)
def cash_requests(request):
    pending_requests = CashAndECashRequest.objects.filter(float_type='Cash', status='Pending').order_by('-created_at')
    context = {
        'pending_requests': pending_requests,
        'title': 'Cash Requests'
    }
    return render(request, 'owner/pay_to/cash_requests.html', context)

def e_cash_requests(request):
    pending_requests = CashAndECashRequest.objects.filter(float_type__in=['Telco'], status='Pending').order_by('-created_at')
    
    context = {
        'pending_requests': pending_requests,

        'title': 'Cash Requests'
    }
    return render(request, 'owner/pay_to/ecash_requests.html', context)

def branch_bank_requests(request):
    pending_requests = CashAndECashRequest.objects.filter(float_type__in=['Bank'], status='Pending').order_by('-created_at')
    
    context = {
        'pending_requests': pending_requests,

        'title': 'Bank Requests'
    }
    return render(request, 'owner/financial_services/bank_deposit.html', context)


@login_required
@user_passes_test(is_owner)
def approve_cash_and_ecash_request(request, request_id):
    request_obj = get_object_or_404(CashAndECashRequest, id=request_id)
    
    account = request_obj.agent.e_float_drawers.filter(date=request_obj.created_at).first()
    
    if not account:
        messages.error(request, 'No e-float account found for this date')
        return redirect('view_payment_requests')
    
    
    request_obj.status = 'Approved'
    request_obj.save()
    account.update_balance_for_cash_and_ecash(request_obj.bank, request_obj.network, request_obj.cash, request_obj.amount, request_obj.status)
    return redirect('cash_requests')

@login_required
@user_passes_test(is_owner)
def approve_bank_requests(request, request_id):
    request_obj = get_object_or_404(CashAndECashRequest, id=request_id)
    
    account = request_obj.agent.e_float_drawers.filter(date=request_obj.created_at).first()
    
    if not account:
        messages.error(request, 'No e-float account found for this date')
        return redirect('view_payment_requests')
    
    if request.method == 'POST':
        owner_transaction_id = request.POST.get('owner_transaction_id')
        if not owner_transaction_id:
            messages.error(request, 'Transaction ID is required.')
            return redirect('approve_branch_bank_request', request_id=request_obj.id)
        # if request_obj.transaction_id != owner_transaction_id:
        #     messages.error(request, 'Transaction ID does not match the Branch\'s input.')
        #     return redirect('approve_branch_bank_request', request_id=request_obj.id)
        request_obj.transaction_id = owner_transaction_id
        request_obj.status = 'Approved'
        request_obj.save()
        account.update_balance_for_cash_and_ecash(request_obj.bank, request_obj.network, request_obj.cash, request_obj.amount, request_obj.status)
        messages.success(request, 'Bank request approved succussfully')
        return redirect('branch_bank_requests')
    context = {
        'request_obj': request_obj
    }
    return render(request, 'owner/financial_services/approve_bank.html', context)
    
    
        

@login_required
@user_passes_test(is_owner)
def reject_cash_and_ecash_request(request, request_id):
    request_obj = get_object_or_404(CashAndECashRequest, id=request_id)
    request_obj.delete()
    messages.success(request, 'Request rejected.')
    return redirect('cash_requests')

@login_required
@user_passes_test(is_owner)
def get_all_agents(request, branch_id):
    agent = Agent.objects.get(id=branch_id)
    context = {
        'agents': agent,
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


# @login_required
# def approve_bank_deposit(request, deposit_id):
#     deposit = get_object_or_404(BankDeposit, id=deposit_id)
#     account = deposit.agent.e_float_drawers.filter(date=deposit.date_deposited).first()
    
#     if not account:
#         messages.error(request, 'No e-float account found for this date')
#         return redirect('bank_deposit_requests')
    
#     # Check if the bank has sufficient balance
#     bank_balance = getattr(account, f"{deposit.bank.lower()}_balance")
#     if deposit.amount > bank_balance:
#         messages.error(request, f'Insufficient balance is {deposit.bank}')
#         return redirect('bank_deposit_requests')
    
    



@login_required
@user_passes_test(is_owner)
def approve_payment(request, payment_id):
    payment = get_object_or_404(PaymentRequest, id=payment_id)
    account = payment.agent.e_float_drawers.filter(date=payment.created_at).first()
    
    if not account:
        messages.error(request, 'No e-float account found for this date')
        return redirect('view_payment_requests')
    
    if request.method == 'POST':
        owner_transaction_id = request.POST.get('owner_transaction_id')
        if not owner_transaction_id:
            messages.error(request, 'Transaction ID is required.')
            return redirect('approve_payment', payment_id=payment.id)
        if payment.branch_transaction_id != owner_transaction_id:
            messages.error(request, 'Transaction ID does not match the Branch\'s input.')
            return redirect('approve_payment', payment_id=payment.id)
        payment.branch_transaction_id = owner_transaction_id
        
    
    # Check if the bank has sufficient balance
    # bank_balance = getattr(account, f"{payment.bank.lower()}_balance")
    # network_balance = getattr(account, f"{payment.network.lower()}_balance")
    
    # if payment.amount > bank_balance:
    #     messages.error(request, f'Insufficient balance is {payment.bank}')
    #     return redirect('view_payment_requests')
    
    # elif payment.amount > network_balance:
    #     messages.error(request, f'Insufficient balance is {payment.network}')
    #     return redirect('view_payment_requests')
    
        payment.status = 'Approved'
        payment.save()
        account.update_balance_for_payments(payment.bank, payment.network, payment.branch, payment.amount, payment.status)
        messages.success(request, 'Payment request approved successfully.')
        return redirect('view_payment_requests')
    
    context = {
        'payment': payment, 
        'title': 'Approve Payment'
    }
    
    return render(request, 'owner/payments/approve_branch_payment.html', context)

@login_required
@user_passes_test(is_owner)
def reject_payment(request, payment_id):
    payment = get_object_or_404(PaymentRequest, id=payment_id)
    payment.delete()
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
    # deposit.status = 'Approved'
    deposit.save()
    account.update_balance_for_bank_deposit(deposit.bank, deposit.amount)
    messages.success(request, 'Bank Deposit approved succussfully')
    return redirect('bank_deposit_requests')

@login_required
def reject_bank_deposit(request, deposit_id):
    deposit = get_object_or_404(BankDeposit, id=deposit_id)
    deposit.delete()
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
    withdrawal.delete()
    messages.success(request, 'Bank Withdrawal rejected')
    return redirect('bank_withdrawal_requests')

# Branches

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

def agentCustomer(request, branch_id):
    branch = get_object_or_404(Agent, id=branch_id)
    customers = Customer.objects.filter(agent=branch)
    context = {
        'customers': customers,
        'title': 'Customers'
    }
    return render(request, 'owner/agent_Detail/agentCustomer.html', context)


def bankDeposit(request, branch_id):
    branch = get_object_or_404(Agent, id=branch_id)
    dates = BankDeposit.objects.filter(agent=branch).values('date_deposited', 'agent').annotate(total_amount=Sum('amount')).order_by('-date_deposited')
    context = {
        'dates': dates,
        'title': 'Bank Deposit'
    }
    return render(request, 'owner/agent_Detail/bankDeposit.html', context)

def bankDepositDetail(request, branch_id, date):
    branch = get_object_or_404(Agent, id=branch_id)
    bank_deposit_transactions = BankDeposit.objects.filter(agent=branch, date_deposited=date).order_by('-date_deposited', '-time_deposited')
    context = {
        'date': date,
        'agent': branch,
        'bank_deposit_transactions': bank_deposit_transactions
    }
    return render(request, 'owner/agent_Detail/bankDepositDetail.html', context)


def delete_agent_bank_deposit(request, deposit_id):
    deposit = BankDeposit.objects.get(id=deposit_id)
    deposit.delete()
    return redirect('delete_transaction_notification')

def bank_withdrawal(request, branch_id):
    branch = get_object_or_404(Agent, id=branch_id)
    dates = BankWithdrawal.objects.filter(agent=branch).values('date_withdrawn', 'agent').annotate(total_amount=Sum('amount')).order_by('-date_withdrawn')
    context = {
        'dates': dates,
        'title': 'Bank Withdrawal'
    }
    return render(request, 'owner/agent_Detail/bank_withdrawal.html', context)

def bank_with_detail(request, branch_id, date):
    branch = get_object_or_404(Agent, id=branch_id)
    bank_withdrawal_transactions = BankWithdrawal.objects.filter(agent=branch, date_withdrawn=date).order_by('-date_withdrawn', '-time_withdrawn')
    context = {
        'date': date,
        'agent': branch,
        'bank_withdrawal_transactions': bank_withdrawal_transactions
    }
    return render(request, 'owner/agent_Detail/bank_with_detail.html', context)

def delete_agent_bank_withdrawal(request, withdrawal_id):
    withdrawal = BankWithdrawal.objects.get(id=withdrawal_id)
    withdrawal.delete()
    return redirect('delete_transaction_notification')

def cash_In(request, branch_id):
    branch = get_object_or_404(Agent, id=branch_id)
    dates = CustomerCashIn.objects.filter(agent=branch).values('date_deposited', 'agent').annotate(total_amount=Sum('amount')).order_by('-date_deposited')
    context = {
        'dates': dates,
        'title': 'Cash In'
    }
    return render(request, 'owner/agent_Detail/cash_In.html', context)

def cash_in_detail(request, branch_id, date):
    branch = get_object_or_404(Agent, id=branch_id)
    cash_in_transactions = CustomerCashIn.objects.filter(agent=branch, date_deposited=date).order_by('-date_deposited', '-time_deposited')
    context = {
        'date': date,
        'agent': branch,
        'cash_in_transactions': cash_in_transactions
    }
    return render(request, 'owner/agent_Detail/cash_in_detail.html', context)  


def delete_agent_cash_ins(request, cash_id):
    cashin = CustomerCashIn.objects.get(id=cash_id)
    cashin.delete()
    return redirect('delete_transaction_notification')


def cash_out_detail(request, branch_id, date):
    branch = get_object_or_404(Agent, id=branch_id)
    cash_out_transactions = CustomerCashOut.objects.filter(agent=branch, date_withdrawn=date).order_by('-date_withdrawn', '-time_withdrawn')
    context = {
        'date': date,
        'agent': branch,
        'cash_out_transactions': cash_out_transactions
    }
    return render(request, 'owner/agent_Detail/cash_out_detail.html', context)  

def cash_out_agent(request, branch_id):
    branch = get_object_or_404(Agent, id=branch_id)
    dates = CustomerCashOut.objects.filter(agent=branch).values('date_withdrawn', 'agent').annotate(total_amount=Sum('amount')).order_by('-date_withdrawn')
    context = {
        'dates': dates,
        'title': 'Cash In'
    }
    return render(request, 'owner/agent_Detail/cash_out_agent.html', context)  

def delete_agent_cash_outs(request, cash_id):
    cashout = CustomerCashOut.objects.get(id=cash_id)
    cashout.delete()
    return redirect('delete_transaction_notification')

def branch_bank_deposit_date(request, branch_id):
    branch = get_object_or_404(Agent, id=branch_id)
    dates = BankDeposit.objects.filter(agent=branch).values('date_deposited', 'agent').annotate(total_amount=Sum('amount')).order_by('-date_deposited')
    context = {
        'dates': dates
    }
    return render(request, 'owner/agent_Detail/bank_deposit_date.html', context)

def branch_bank_deposit_transaction(request, branch_id, date):
    branch = get_object_or_404(Agent, id=branch_id)
    bank_deposit_transactions = BankDeposit.objects.filter(agent=branch, date_deposited=date).order_by('-date_deposited', '-time_deposited')
    context = {
        'date': date,
        'agent': branch,
        'bank_deposit_transactions': bank_deposit_transactions
    }
    return render(request, 'owner/agent_Detail/bank_deposit_transaction.html', context)

def delete_agent_bank_deposit(request, deposit_id):
    deposit = BankDeposit.objects.get(id=deposit_id)
    deposit.delete()
    return redirect('delete_transaction_notification')

@login_required
def branch_bank_withdrawal_transactions_date(request, branch_id):
    branch = get_object_or_404(Agent, id=branch_id)
    dates = BankWithdrawal.objects.filter(agent=branch).values('date_withdrawn', 'agent').annotate(total_amount=Sum('amount')).order_by('-date_withdrawn')
    context = {
        'dates': dates
    }
    return render(request, 'owner/agent_Detail/bank_withdrawal_date.html', context)

def branch_bank_withdrawal_transactions(request, branch_id, date):
    branch = get_object_or_404(Agent, id=branch_id)
    bank_withdrawal_transactions = BankWithdrawal.objects.filter(agent=branch, date_withdrawn=date).order_by('-date_withdrawn', '-time_withdrawn')
    context = {
        'date': date,
        'agent': branch,
        'bank_withdrawal_transactions': bank_withdrawal_transactions
    }
    return render(request, 'owner/agent_Detail/bank_withdrawal_transaction.html', context)

def delete_branch_bank_withdrawal(request, withdrawal_id):
    withdrawal = BankWithdrawal.objects.get(id=withdrawal_id)
    withdrawal.delete()
    return redirect('delete_transaction_notification')


@login_required
def branch_ecash_transactions_date(request, branch_id):
    branch = get_object_or_404(Agent, id=branch_id)
    dates = CashAndECashRequest.objects.filter(agent=branch).values('created_at', 'agent').annotate(total_amount=Sum('amount')).order_by('-created_at')
    context = {
        'dates': dates
    }
    return render(request, 'owner/agent_Detail/ecash_date.html', context)

def branch_ecash_transactions(request, branch_id, date):
    branch = get_object_or_404(Agent, id=branch_id)
    ecash_transactions = CashAndECashRequest.objects.filter(agent=branch, created_at=date).order_by('-created_at')
    context = {
        'date': date,
        'agent': branch,
        'ecash_transactions': ecash_transactions
    }
    return render(request, 'owner/agent_Detail/ecash_transaction.html', context)

def delete_branch_ecash(request, ecash_id):
    ecash = CashAndECashRequest.objects.get(id=ecash_id)
    ecash.delete()
    return redirect('delete_transaction_notification')

@login_required
def branch_payment_transactions_date(request, branch_id):
    branch = get_object_or_404(Agent, id=branch_id)
    dates = PaymentRequest.objects.filter(agent=branch).values('created_at', 'agent').annotate(total_amount=Sum('amount')).order_by('-created_at')
    context = {
        'dates': dates
    }
    return render(request, 'owner/agent_Detail/payment_date.html', context)

def branch_payment_transactions(request, branch_id, date):
    branch = get_object_or_404(Agent, id=branch_id)
    payment_transactions = PaymentRequest.objects.filter(agent=branch, status='Approved', created_at=date).order_by('-created_at')
    context = {
        'date': date,
        'agent': branch,
        'payment_transactions': payment_transactions
    }
    return render(request, 'owner/agent_Detail/payment_transaction.html', context)

def delete_branch_payment(request, payment_id):
    payment = PaymentRequest.objects.get(id=payment_id)
    payment.delete()
    return redirect('delete_transaction_notification')

def pay_to(request):
    return render(request, 'owner/agent_Detail/pay_to.html')  

def all_transaction(request):
    return render(request, 'owner/agent_Detail/all_transaction.html')  

@login_required
@user_passes_test(is_owner)
def branch_report_view(request, branch_id):
    branch = get_object_or_404(Agent, id=branch_id)
    reports = BranchReport.objects.filter(branch=branch)
    context = {
        'reports': reports,
        'title': 'Reports'
    }
    return render(request, 'owner/reports/branch_report.html', context) 

def commission(request):
    filter_type = request.GET.get('filter', 'daily') # Default to daily
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if filter_type == 'daily':
        cashincommissions = CashInCommission.objects.filter(date=datetime.today())
        cashoutcommissions = CashOutCommission.objects.filter(date=datetime.today())
    elif filter_type == 'monthly':
        start_of_month = datetime.today().replace(day=1)
        cashincommissions = CashInCommission.objects.filter(date__gte=start_of_month, date__lte=datetime.today())
        cashoutcommissions = CashOutCommission.objects.filter(date__gte=start_of_month, date__lte=datetime.today())
    elif start_date and end_date:
        cashincommissions = CashInCommission.objects.filter(date__gte=start_date, date__lte=end_date)
        cashoutcommissions = CashOutCommission.objects.filter(date__gte=start_date, date__lte=end_date)
    else:
        cashincommissions = CashInCommission.objects.none()
        cashoutcommissions = CashOutCommission.objects.none()
        
    # Calculate totals
    cashin_total_amount = sum(cashincommission.customer_cash_in.amount for cashincommission in cashincommissions)
    cashout_total_amount = sum(cashoutcommission.customer_cash_out.amount for cashoutcommission in cashoutcommissions)
    
    total_cash_received = sum(cashincommission.customer_cash_in.cash_received for cashincommission in cashincommissions)
    total_cash_paid = sum(cashoutcommission.customer_cash_out.cash_paid for cashoutcommission in cashoutcommissions)
    
    cash_in_total_commission = cashincommissions.aggregate(Sum('amount'))['amount__sum'] or 0
    cash_out_total_commission = cashoutcommissions.aggregate(Sum('amount'))['amount__sum'] or 0
    
    all_total_commission = cash_in_total_commission + cash_out_total_commission
    
    context = {
        'all_total_commission': all_total_commission,
        'cashin_total_amount': cashin_total_amount,
        'cashout_total_amount': cashout_total_amount,
        'total_cash_received': total_cash_received,
        'total_cash_paid': total_cash_paid,
        'cash_in_total_commission': cash_in_total_commission,
        'cash_out_total_commission': cash_out_total_commission,
        'cashincommissions': cashincommissions,
        'cashoutcommissions': cashoutcommissions,
        'filter_type': filter_type,
        'title': 'Commission'
    }
    return render(request, 'owner/agent_Detail/commission.html', context)

def branch_balance(request, branch_id):
    branch = get_object_or_404(Agent, id=branch_id)
    
    total_requests = CashAndECashRequest.total_ecash_for_customer(agent=branch, status='Approved')
    total_payments = PaymentRequest.total_payment_for_customer(agent=branch, status='Approved')
    
    balance_left = total_payments - total_requests
    
    context = {
        'branch': branch,
        'cumulative_requests': total_requests,
        'cumulative_payments': total_payments,
        'cumulative_balance': balance_left,

        'title': 'Account Balance'
    }
    return render(request, 'owner/agent_Detail/branch_balance.html', context)

@login_required
@user_passes_test(is_owner)
def complains(request):
    complains = CustomerComplain.objects.all()
    context = {
        'complains': complains,
        'title': 'Complains'
    }
    return render(request, 'owner/customerCare/complains.html', context)  

@login_required
@user_passes_test(is_owner)
def fraud(request):
    frauds = CustomerFraud.objects.all()
    context = {
        'frauds': frauds,
        'title': 'Frauds'
    }
    return render(request, 'owner/customerCare/fraud.html', context)


@login_required
@user_passes_test(is_owner)
def hold_account(request):
    hold_accounts = HoldCustomerAccount.objects.all()
    context = {
        'hold_accounts': hold_accounts,
        'title': 'Hold Account'
    }
    return render(request, 'owner/customerCare/holdAccount.html', context)  


# def register_mobilization(request):
#     users = User.objects.filter(role='MOBILIZATION')
#     branches = Branch.objects.all()
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         branch_id = request.POST.get('branch')
#         email = request.POST.get('email')
#         full_name = request.POST.get('full_name')
#         phone_number = request.POST.get('phone_number')
#         company_name = request.POST.get('company_name')
#         company_phone = request.POST.get('customer_phone')
#         digital_address = request.POST.get('digital_address')
#         mobilization_code = request.POST.get('mobilization_code')
#         password = request.POST.get('password')
        
#         # Validate required fields
#         if not (username and password and phone_number and full_name and branch_id):
#             messages.error(request, 'Please fill in all required fields.')
#             return redirect('register_mobilization')
        
#         # Check if the username already exists
#         if User.objects.filter(username=username).exists():
#             messages.error(request, 'Username already taken.')
#             return redirect('register_mobilization')
        
#         # Check if the phone number already exists
#         if User.objects.filter(phone_number=phone_number).exists():
#             messages.error(request, 'Phone number already registered.')
#             return redirect('register_mobilization')
        
#         # Create the user
#         user = User.objects.create(
#             username=username,
#             password=make_password(password),  # Hash the password
#             phone_number=phone_number,
#             role='MOBILIZATION',
#             is_approved=True  # Automatically approve customers
#         )
        
#         # user = get_object_or_404(User, id=customer_id)
#         branch = get_object_or_404(Branch, id=branch_id)
        
#         # agent = Agent.objects.get(user=request.user)
        
#         Mobilization.objects.create(
#             user=user,
#             owner=request.user.owner,  # Assign the current owner
#             branch=branch,
#             email=email,
#             full_name=full_name,
#             phone_number=phone_number,
#             company_name=company_name,
#             company_number=company_phone,
#             digital_address=digital_address,
#             mobilization_code=mobilization_code,
#         )
#         messages.success(request, 'Mobilization registered successfully!')
#         return redirect('register_mobilization')
        
#     context = {
# #         # 'users': users,
#         'branches': branches,
#         'title': 'Mobilization Registration'
#     }
#     return render(request, 'owner/mobilization/register_mobilization.html', context)

@login_required
def mobilization_bank_deposit_requests(request):
    phone_numbers = bank_deposits.objects.filter(status='Pending').values_list('phone_number', flat=True).distinct()
    customers = {c.phone_number: c for c in Customer.objects.filter(phone_number__in=phone_numbers)}
    pending_deposits = bank_deposits.objects.filter(status='Pending').order_by('-date_deposited', '-time_deposited')
    context = {
        'pending_deposits': pending_deposits,
        'customer_map': customers,
        'title': 'Bank Deposit Requests'
    }
    return render(request, 'owner/mobilization_approvals/bank_deposit.html', context)

@login_required
def approve_mobilization_bank_deposit(request, deposit_id):
    deposit = get_object_or_404(bank_deposits, id=deposit_id)
    if request.method == 'POST':
        owner_transaction_id = request.POST.get('owner_transaction_id')
        if not owner_transaction_id:
            messages.error(request, 'Transaction ID is required.')
            return redirect('approve_mobilization_bank_deposit', deposit_id=deposit.id)
        deposit.owner_transaction_id = owner_transaction_id
        deposit.status = 'Approved'
        deposit.save()
        messages.success(request, 'Bank Deposit approved succussfully')
        return redirect('mobilization_bank_deposit_requests')
    context = {
        'deposit': deposit
    }
    return render(request, 'owner/mobilization_approvals/bank_deposit_approval.html', context)

@login_required
def reject_mobilization_bank_deposit(request, deposit_id):
    deposit = get_object_or_404(bank_deposits, id=deposit_id)
    # deposit.status = 'Rejected'
    deposit.delete()
    messages.success(request, 'Bank Deposit rejected')
    return redirect('mobilization_bank_deposit_requests')

@login_required
def update_mobilization_bank_deposit(request, deposit_id):
    deposit = get_object_or_404(bank_deposits, id=deposit_id)
    
    if request.method == 'POST':
        form = BankDepositForm(request.POST, instance=deposit)
        if form.is_valid():
            updated_deposit = form.save(commit=False)
            updated_deposit.save()
            messages.success(request, 'Bank Deposit Updated Successfully.')
            return redirect('update_mobilization_bank_deposit', deposit=deposit.id)
    else:
        form = BankDepositForm(instance=deposit)
    context = {
        'form': form,
        'deposit': deposit,
        'title': 'Update Bank Deposit'
    }
    return render(request, 'owner/mobilization/update_bank_deposit.html', context)
        

@login_required
def mobilization_bank_withdrawal_requests(request):
    pending_withdrawals = bank_withdrawals.objects.filter(status='Pending').order_by('-date_withdrawn', '-time_withdrawn')
    context = {
        'pending_withdrawals': pending_withdrawals,
        'title': 'Bank Withdrawal Requests'
    }
    return render(request, 'owner/mobilization_approvals/bank_withdrawal.html', context)

@login_required
def approve_mobilization_withdrawal(request, withdrawal_id):
    withdrawal = get_object_or_404(bank_withdrawals, id=withdrawal_id)
    # withdrawal.status = 'Approved'
    withdrawal.delete()
    messages.success(request, 'Bank Withdrawal approved succussfully')
    return redirect('mobilization_bank_withdrawal_requests')

@login_required
def reject_mobilization_withdrawal(request, withdrawal_id):
    withdrawal = get_object_or_404(bank_withdrawals, id=withdrawal_id)
    # withdrawal.status = 'Rejected'
    withdrawal.delete()
    messages.success(request, 'Bank Withdrawal rejected')
    return redirect('mobilization_bank_withdrawal_requests')

@login_required
def mobilization_payment_requests(request):
    payments = payment_requests.objects.filter(status='Pending').order_by('-created_at')
    
    context = {
        'payments': payments,
        'title': 'Payment Requests'
    }
    return render(request, 'owner/mobilization_approvals/payment.html', context)


@login_required
def approve_mobilization_payment(request, payment_id):
    payment = get_object_or_404(payment_requests, id=payment_id)
    if request.method == 'POST':
        owner_transaction_id = request.POST.get('owner_transaction_id')
        if not owner_transaction_id:
            messages.error(request, 'Transaction ID is required.')
            return redirect('approve_mobilization_payment', payment_id=payment.id)
        if payment.mobilization_transaction_id != owner_transaction_id:
            messages.error(request, 'Transaction ID does not match the Mobilization\'s input.')
            return redirect('approve_mobilization_payment', payment_id=payment.id)
        payment.transaction_id = owner_transaction_id
        payment.status = 'Approved'
        payment.save()
        messages.success(request, 'Payment approved succussfully')
        return redirect('mobilization_payment_requests')
    context = {
        'payment': payment
    }
    return render(request, 'owner/mobilization_approvals/payment_approval.html', context)

@login_required
def reject_mobilization_payment(request, payment_id):
    payment = get_object_or_404(payment_requests, id=payment_id)
    # payment.status = 'Rejected'
    payment.delete()
    messages.success(request, 'Payment rejected')
    return redirect('mobilization_payment_requests')





def mobilization_agent_detail(request, mobilization_id):
    mobilization = get_object_or_404(Mobilization, id=mobilization_id)
    context = {
        'mobilization': mobilization
    }
    return render(request, 'owner/mobilization/mobilization_detail.html', context)

def mobilization_customers(request, mobilization_id):
    mobilization = get_object_or_404(Mobilization, id=mobilization_id)
    customers = Customer.objects.filter(mobilization=mobilization)
    context = {
        'customers': customers,
        'title': 'Customers'
    }
    return render(request, 'owner/mobilization/customers.html', context)


def delete_mobilization_customer(request, mobilization_id):
    
    customer = Customer.objects.get(id=mobilization_id)
    customer.delete()
    return redirect("mobilization_customers", customer=customer.id)


# def update_mobilization_customer(request, mobilization_id):
#     customer = Customer.objects.get(id=mobilization_id)
#     if request.method == 'POST':
#         form = CustomerUpdateForm(request.POST, request.FILES, instance=customer)
#         if form.is_valid():
#             updated_customer = form.save(commit=False)
#             updated_customer.save()
#             messages.success(request, 'Customer updated successfully!')
#             return redirect('update_mobilization_customer', mobilization=customer.id)
#     else:
#         form = CustomerUpdateForm(instance=customer)
        
#     context = {
#         'form': form,
#         'title': 'Update Customer'
#     }
        
#     return render(request, 'owner/mobilization/customer_update.html', context)

def mobilization_all_transactions(requests):
    context = {
        'title': 'All Transactions'
    }
    return render(requests, 'owner/mobilization/all_transactions.html', context)

@login_required
@user_passes_test(is_owner)
def mobilization_report_view(request, mobilization_id):
    mobilization = get_object_or_404(Mobilization, id=mobilization_id)
    reports = mobilization_reports.objects.filter(mobilization=mobilization)
    context = {
        'reports': reports,
        'title': 'Reports'
    }
    return render(request, 'owner/reports/mobilization_report.html', context) 

def mobilization_account_detail(request, mobilization_id):
    mobilization = get_object_or_404(Mobilization, id=mobilization_id)
    # today = timezone.now().date()
    today = timezone.now().date() - timedelta(days=30)
    
    # account = get_object_or_404(MobilizationAccount, mobilization=mobilization)
    
    total_deposits = bank_deposits.total_bank_deposit_for_customer(mobilization=mobilization, status='Approved')
    total_payments = payment_requests.total_payment_for_customer(mobilization=mobilization, status='Approved')
    
    balance_left = total_payments - total_deposits
    context = {
        # 'account': account,
        'mobilization': mobilization,
        'total_deposits': total_deposits,
        'total_payments': total_payments,
        'balance_left': balance_left,
        'title': 'Account'
    }
    return render(request, 'owner/mobilization/account.html', context)

# def add_mobilization_account(request, mobilization_id):
#     mobilization = get_object_or_404(Mobilization, id=mobilization_id)

    
#     # Check if an e-float drawer already exists for today
#     account = MobilizationAccount.objects.filter(mobilization=mobilization).first()

#     if request.method == 'POST':
#         form = MobilizationAccountForm(request.POST, instance=account)
#         if form.is_valid():
#             form.save()
#             return redirect('mobilization_account_detail', mobilization.id)
#     else:
#         form = MobilizationAccountForm(instance=account)
        
#     context = {
#         'mobilization': mobilization,
#         'form': form,
#         'title': 'Mobilization Account'
#     }
#     return render(request, 'owner/mobilization/mobilization_account.html', context)


@login_required
def mobilization_bank_deposit_transactions_date(request, mobilization_id):
    mobilization = get_object_or_404(Mobilization, id=mobilization_id)
    dates = bank_deposits.objects.filter(mobilization=mobilization).values('date_deposited', 'mobilization').annotate(total_amount=Sum('amount')).order_by('-date_deposited')
    context = {
        'dates': dates
    }
    return render(request, 'owner/mobilization/bank_deposit_transaction_date.html', context)

 
@login_required
def mobilization_bank_deposit_transactions(request, mobilization_id, date):
    mobilization = get_object_or_404(Mobilization, id=mobilization_id)
    bank_deposit_transactions = bank_deposits.objects.filter(mobilization=mobilization, status='Approved', date_deposited=date).order_by('-date_deposited', '-time_deposited')
    context = {
        'date': date,
        'mobilization': mobilization,
        'bank_deposit_transactions': bank_deposit_transactions
    }
    return render(request, 'owner/mobilization/bank_deposit_transactions.html', context)


def delete_mobilization_bank_deposit(request, deposit_id):
    deposit = bank_deposits.objects.get(id=deposit_id)
    deposit.delete()
    return redirect('delete_transaction_notification')


def delete_transaction_notification(request):
    return render(request, 'owner/message/message.html')
 

@login_required
def mobilization_bank_withdrawal_transactions_date(request, mobilization_id):
    mobilization = get_object_or_404(Mobilization, id=mobilization_id)
    dates = bank_withdrawals.objects.filter(mobilization=mobilization).values('date_withdrawn', 'mobilization').annotate(total_amount=Sum('amount')).order_by('-date_withdrawn')
    context = {
        'dates': dates
    }
    return render(request, 'owner/mobilization/bank_withdrawal_transaction_date.html', context)

def mobilization_bank_withdrawal_transactions(request, mobilization_id, date):
    mobilization = get_object_or_404(Mobilization, id=mobilization_id)
    bank_withdrawal_transactions = bank_withdrawals.objects.filter(mobilization=mobilization, status='Approved', date_withdrawn=date).order_by('-date_withdrawn', '-time_withdrawn')
    context = {
        'date': date,
        'mobilization': mobilization,
        'bank_withdrawal_transactions': bank_withdrawal_transactions
    }
    return render(request, 'owner/mobilization/bank_withdrawal_transactions.html', context)

def delete_mobilization_bank_withdrawal(request, withdrawal_id):
    withdrawal = bank_withdrawals.objects.get(id=withdrawal_id)
    withdrawal.delete()
    return redirect('delete_transaction_notification')


@login_required
def mobilization_payment_transactions_date(request, mobilization_id):
    mobilization = get_object_or_404(Mobilization, id=mobilization_id)
    dates = payment_requests.objects.filter(mobilization=mobilization).values('created_at', 'mobilization').annotate(total_amount=Sum('amount')).order_by('-created_at')
    context = {
        'dates': dates
    }
    return render(request, 'owner/mobilization/payment_transaction_date.html', context)

def mobilization_payment_transactions(request, mobilization_id, date):
    mobilization = get_object_or_404(Mobilization, id=mobilization_id)
    payment_transactions = payment_requests.objects.filter(mobilization=mobilization, status='Approved', created_at=date).order_by('-created_at')
    context = {
        'date': date,
        'mobilization': mobilization,
        'payment_transactions': payment_transactions
    }
    return render(request, 'owner/mobilization/payment_transactions.html', context)

def delete_mobilization_payment(request, payment_id):
    payment = payment_requests.objects.get(id=payment_id)
    payment.delete()
    return redirect('delete_transaction_notification')

@login_required
def update_mobilization_payment(request, payment_id):
    payment = get_object_or_404(payment_requests, id=payment_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            updated_payment = form.save(commit=False)
            updated_payment.save()
            messages.success(request, 'Payment Updated Successfully.')
            return redirect('mobilization_payment_requests')
    else:
        form = PaymentForm(instance=payment)
    context = {
        'form': form,
        'payment': payment,
        'title': 'Update Payment'
    }
    return render(request, 'owner/mobilization/update_payment.html', context)
        

def all_transaction(request):
    return render(request, 'owner/agent_Detail/all_transaction.html')


def all_filters(request):
    return render(request, 'owner/filters/filters.html')

def filter_bank_by_branch_bank_deposit(request):
    # Get all unique bank names from the BankDeposit model
    banks = BankDeposit.objects.order_by('bank').values_list('bank', flat=True).distinct()
    
    # Get selected bank from request GET parameters
    selected_bank = request.GET.get('bank')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
     # Filter transactions based on selected bank
    transactions = BankDeposit.objects.all()
    if selected_bank:
        transactions = transactions.filter(bank=selected_bank)
    if start_date:
        transactions = transactions.filter(date_deposited__gte=start_date)
    if end_date:
        transactions = transactions.filter(date_deposited__lte=end_date)
        
    # Calculate total amount of filtered transactions
    total_amount = transactions.aggregate(total=Sum('amount'))['total'] or 0
        
    context = {
        'transactions': transactions,
        'banks': banks,
        'selected_bank': selected_bank,
        'start_date': start_date,
        'end_date': end_date,
        'total_amount': total_amount
    }
    
    return render(request, 'owner/filters/branch_bank_deposit_filter.html', context)


def filter_bank_by_branch_payment(request):
    # Get all unique bank names from the BankDeposit model
    banks = PaymentRequest.objects.order_by('bank').values_list('bank', flat=True).distinct()
    networks = PaymentRequest.objects.order_by('network').values_list('network', flat=True).distinct()
    branches = PaymentRequest.objects.order_by('branch').values_list('branch', flat=True).distinct()
    
    # Get selected bank from request GET parameters
    selected_bank = request.GET.get('bank')
    selected_network = request.GET.get('network')
    selected_branch = request.GET.get('branch')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
     # Filter transactions based on selected bank
    transactions = PaymentRequest.objects.all()
    if selected_bank:
        transactions = transactions.filter(bank=selected_bank)
    if selected_network:
        transactions = transactions.filter(network=selected_network)
    if selected_branch:
        transactions = transactions.filter(branch=selected_branch)
    if start_date:
        transactions = transactions.filter(created_at__gte=start_date)
    if end_date:
        transactions = transactions.filter(created_at__lte=end_date)
        
    # Calculate total amount of filtered transactions
    total_amount = transactions.aggregate(total=Sum('amount'))['total'] or 0
        
    context = {
        'transactions': transactions,
        'banks': banks,
        'networks': networks,
        'branches': branches,
        'selected_bank': selected_bank,
        'selected_network': selected_network,
        'selected_branch': selected_branch,
        'start_date': start_date,
        'end_date': end_date,
        'total_amount': total_amount
    }
    
    return render(request, 'owner/filters/branch_payment_filter.html', context)


def filter_bank_by_mobilization_bank_deposit(request):
    # Get all unique bank names from the BankDeposit model
    banks = bank_deposits.objects.order_by('bank').values_list('bank', flat=True).distinct()
    
    # Get selected bank from request GET parameters
    selected_bank = request.GET.get('bank')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
     # Filter transactions based on selected bank
    transactions = bank_deposits.objects.all()
    if selected_bank:
        transactions = transactions.filter(bank=selected_bank)
    if start_date:
        transactions = transactions.filter(date_deposited__gte=start_date)
    if end_date:
        transactions = transactions.filter(date_deposited__lte=end_date)
        
    # Calculate total amount of filtered transactions
    total_amount = transactions.aggregate(total=Sum('amount'))['total'] or 0
        
    context = {
        'transactions': transactions,
        'banks': banks,
        'selected_bank': selected_bank,
        'start_date': start_date,
        'end_date': end_date,
        'total_amount': total_amount
    }
    
    return render(request, 'owner/filters/mobilization_bank_deposit_filter.html', context)


def filter_bank_by_ecash(request):
    # Get all unique bank names from the BankDeposit model
    banks = CashAndECashRequest.objects.order_by('bank').values_list('bank', flat=True).distinct()
    networks = CashAndECashRequest.objects.order_by('network').values_list('network', flat=True).distinct()
    cashes = CashAndECashRequest.objects.order_by('cash').values_list('cash', flat=True).distinct()
    
    # Get selected bank from request GET parameters
    selected_bank = request.GET.get('bank')
    selected_network = request.GET.get('network')
    selected_cash = request.GET.get('cash')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
     # Filter transactions based on selected bank
    transactions = CashAndECashRequest.objects.all()
    if selected_bank:
        transactions = transactions.filter(bank=selected_bank)
    if selected_network:
        transactions = transactions.filter(network=selected_network)
    if selected_cash:
        transactions = transactions.filter(cash=selected_cash)
    if start_date:
        transactions = transactions.filter(created_at__gte=start_date)
    if end_date:
        transactions = transactions.filter(created_at__lte=end_date)
        
    # Calculate total amount of filtered transactions
    total_amount = transactions.aggregate(total=Sum('amount'))['total'] or 0
        
    context = {
        'transactions': transactions,
        'banks': banks,
        'networks': networks,
        'cashes': cashes,
        'selected_bank': selected_bank,
        'selected_network': selected_network,
        'selected_cash': selected_cash,
        'start_date': start_date,
        'end_date': end_date,
        'total_amount': total_amount
    }
    
    return render(request, 'owner/filters/cash_and_ecash.html', context)


def filter_bank_by_mobilization_payment(request):
    # Get all unique bank names from the BankDeposit model
    banks = payment_requests.objects.order_by('bank').values_list('bank', flat=True).distinct()
    networks = payment_requests.objects.order_by('network').values_list('network', flat=True).distinct()
    branches = payment_requests.objects.order_by('branch').values_list('branch', flat=True).distinct()
    
    # Get selected bank from request GET parameters
    selected_bank = request.GET.get('bank')
    selected_network = request.GET.get('network')
    selected_branch = request.GET.get('branch')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
     # Filter transactions based on selected bank
    transactions = payment_requests.objects.all()
    if selected_bank:
        transactions = transactions.filter(bank=selected_bank)
    if selected_network:
        transactions = transactions.filter(network=selected_network)
    if selected_branch:
        transactions = transactions.filter(branch=selected_branch)
    if start_date:
        transactions = transactions.filter(created_at__gte=start_date)
    if end_date:
        transactions = transactions.filter(created_at__lte=end_date)
        
    # Calculate total amount of filtered transactions
    total_amount = transactions.aggregate(total=Sum('amount'))['total'] or 0
        
    context = {
        'transactions': transactions,
        'banks': banks,
        'networks': networks,
        'branches': branches,
        'selected_bank': selected_bank,
        'selected_network': selected_network,
        'selected_branch': selected_branch,
        'start_date': start_date,
        'end_date': end_date,
        'total_amount': total_amount
    }
    
    return render(request, 'owner/filters/mobilization_payment.html', context)
