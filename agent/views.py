from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.models import User, Branch, Customer, Agent
from banking.forms import DrawerDepositForm, EFloatAccountForm
from banking.models import Bank, CustomerAccount, Drawer, EFloatAccount
from django.utils import timezone
from django.contrib import messages
from .models import CustomerCashIn, CustomerCashOut
from decimal import Decimal

@login_required
def open_e_float_account(request):
    agent = request.user.agent
    today = timezone.now().date()
    
    account, create = EFloatAccount.objects.get_or_create(
        agent=agent,
        date=today,
        defaults={
            'mtn_balance': 0.00,
            'telecel_balance': 0.00,
            'airtel_tigo_balance': 0.00,
            'ecobank_balance': 0.00,
            'fidelity_balance': 0.00,
            'calbank_balance': 0.00,
            'gtbank_balance': 0.00,
            'access_bank_balance': 0.00,
            'cash_at_hand': 0.00
        }
    )
    
    if request.method == 'POST':
        form = EFloatAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, 'E-float account updated succussfully.')
            return redirect('open_efloat_account')
    else:
        form = EFloatAccountForm(instance=account)
        
    context = {
        'form': form,
        'title': 'Open Account'
    }
        
    return render(request, 'agent/efloat_account.html', context)


def view_e_float_account(request):
    agent = request.user.agent
    today = timezone.now().date()
    
    account = get_object_or_404(EFloatAccount, agent=agent, date=today)
    
    context = {
        'account': account,
        'title': ' View Account'
    }
    
    return render(request, 'agent/view_efloat_account.html', context)
    
    
# @login_required
# def open_drawer(request):
#     agent = request.user.agent
#     today = timezone.now().date()
    
#     drawer, created = Drawer.objects.get_or_create(
#         agent=agent,
#         date=today,
#         defaults={'opening_balance': 0.00}
#     )
    
#     if request.method == 'POST':
#         form = DrawerDepositForm(request.POST, instance=drawer)
#         if form.is_valid():
#             form.save()
#             return redirect('agent-dashboard')
#     else:
#         form = DrawerDepositForm(instance=drawer)
        
#     context = {
#         'form': form,
#         'title': 'Drawer'
#     }
    
#     return render(request, 'agent/open_drawer.html', context)

# @login_required
# def close_drawer(request):
#     agent = request.user.agent
#     today = timezone.now().date()
    
#     # Get today's drawer
#     drawer = get_object_or_404(Drawer, agent=agent, date=today, is_closed=False)
    
#     if request.method == 'POST':
#         closing_balance = request.POST.get('closing_balance')
#         drawer.closing_balance = closing_balance
#         drawer.is_closed = True
#         drawer.save()
#         return redirect('agent-dashboard')
    
#     context = {
#         'drawer': drawer,
#         'title': 'Close Drawer'
#     }
    
#     return render(request, 'agent/close_drawer.html', context)

def agent_dashboard(request):
    return render(request, 'agent/dashboard.html')


@login_required
def cashIn(request):
    agent = request.user.agent
    today = timezone.now().date()
    
    
    account = get_object_or_404(EFloatAccount, agent=agent, date=today)
    
    if request.method == 'POST':
        network = request.POST.get('network')
        customer_phone = request.POST.get('customer_phone')
        deposit_type = request.POST.get('deposit_type')
        depositor_name = request.POST.get('depositor_name')
        depositor_number = request.POST.get('depositor_number')
        amount = request.POST.get('amount')
        

        
        cash_in = CustomerCashIn(network=network, customer_phone=customer_phone, deposit_type=deposit_type, depositor_name=depositor_name, depositor_number=depositor_number, amount=amount)
        
        cash_in.agent = agent.user
        

        
        network_balance = getattr(account, f"{cash_in.network.lower()}_balance")
        get_amount = Decimal(cash_in.amount)
        if get_amount > Decimal(network_balance):
            messages.error(request, f"Insufficient balance in {cash_in.network}.")
            return redirect('cashIn')
    
        cash_in.save()
        account.update_balance_for_cash_in(cash_in.network, cash_in.amount)
        messages.success(request, 'Customer Cash-In recorded succussfully.')
        return redirect('agent-dashboard')
    context = {
        'title': 'Cash In'
    }
    return render(request, 'agent/cashIn.html', context)


@login_required
def cashOut(request):
    agent = request.user.agent
    today = timezone.now().date()
    
    
    account = get_object_or_404(EFloatAccount, agent=agent, date=today)
    
    if request.method == 'POST':
        network = request.POST.get('network')
        customer_phone = request.POST.get('customer_phone')
        amount = request.POST.get('amount')
        

        
        cash_out = CustomerCashOut(network=network, customer_phone=customer_phone, amount=amount)
        
        cash_out.agent = agent.user
        

        
        # network_balance = getattr(account, f"{cash_out.network.lower()}_balance")
        cash_at_hand = Decimal(account.cash_at_hand)
        get_amount = Decimal(cash_out.amount)
        if get_amount > cash_at_hand:
            messages.error(request, f"Insufficient balance in {cash_out.network}.")
            return redirect('cashout')
    
        cash_out.save()
        account.update_balance_for_cash_out(cash_out.network, cash_out.amount)
        messages.success(request, 'Customer Cash-Out recorded succussfully.')
        return redirect('agent-dashboard')
    context = {
        'title': 'Cash Out'
    }
    return render(request, 'agent/cashOut.html', context)

# Bank Deposit
@login_required
def agencyBank(request):
    return render(request, 'agent/agencyBank.html')

def withdrawal(request):
    return render(request, 'agent/withdrawal.html')

def TotalTransactionSum(request):
    return render(request, 'agent/TotalTransactionSum.html')

def PaymentSummary(request):
    return render(request, 'agent/PaymentSummary.html')

def customerReg(request):
    users = User.objects.filter(role='CUSTOMER')
    branches = Branch.objects.all()
    if request.method == 'POST':
        customer_id = request.POST['username']
        branch_id = request.POST['branch']
        phone_number = request.POST['phone_number']
        full_name = request.POST['full_name']
        customer_location = request.POST['customer_location']
        digital_address = request.POST['digital_address']
        id_type = request.POST['id_type']
        id_number = request.POST['id_number']
        date_of_birth = request.POST['date_of_birth']
        customer_picture = request.FILES['customer_picture']
        
        user = get_object_or_404(User, id=customer_id)
        branch = get_object_or_404(Branch, id=branch_id)
        agent = Agent.objects.get(user=request.user)
        
        customers = Customer(user=user, agent=agent, branch=branch, phone_number=phone_number, full_name=full_name, customer_location=customer_location, digital_address=digital_address, id_type=id_type, id_number=id_number, date_of_birth=date_of_birth, customer_picture=customer_picture)
        
        customers.save()
        
        return redirect('customerReg')

    context = {
        'users': users,
        'branches': branches,
        'title': 'Customer Registration'
    }
    return render(request, 'agent/customerReg.html', context)

def accountReg(request):
    banks = Bank.objects.all()
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        account_number = request.POST['account_number']
        account_name = request.POST['account_name']
        bank_id = request.POST['bank']
        
        bank = get_object_or_404(Bank, id=bank_id)
        
        customer_accounts = CustomerAccount(account_number=account_number, account_name=account_name, bank=bank, phone_number=phone_number)
        
        try:
            customer = Customer.objects.get(phone_number=phone_number)
            customer_accounts.customer = customer
            customer_accounts.save()
            return redirect('accountReg')
        except Customer.DoesNotExist:
            messages.error(request, 'Customer with this phone number does not exist.')
        
    context = {
        'banks': banks,
        'title': 'Account Registration'
    }
    return render(request, 'agent/accountReg.html', context)

def payment(request):
    return render(request, 'agent/payment.html')

def cashFloatRequest(request):
    return render(request, 'agent/cashFloatRequest.html')

def calculate(request):
    return render(request, 'agent/calculate.html')