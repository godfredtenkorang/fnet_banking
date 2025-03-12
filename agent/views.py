from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from users.models import User, Branch, Customer, Agent
from banking.forms import DrawerDepositForm, EFloatAccountForm
from banking.models import Bank, CustomerAccount, Drawer, EFloatAccount, CustomerPaymentAtBank
from django.utils import timezone
from django.contrib import messages
from .models import CustomerCashIn, CustomerCashOut, BankDeposit, BankWithdrawal, CashAndECashRequest, PaymentRequest, CustomerComplain, HoldCustomerAccount, CustomerFraud, CustomerPayTo, CashInCommission, CashOutCommission
from datetime import datetime, timedelta, date
from decimal import Decimal
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from django.db.models import Sum
from django.core.paginator import Paginator

def is_agent(user):
    return user.role == 'BRANCH'

@login_required
@user_passes_test(is_agent)
def open_e_float_account(request):
    agent = request.user.agent
    today = timezone.now().date()
    
    # Check if an e-float drawer already exists for today
    account = EFloatAccount.objects.filter(agent=agent, date=today).first()
    
    if not account:
        # Create a new drawer for today, carrying forward the fixed capital
        account = EFloatAccount.create_new_drawer(agent)
    
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
        'account': account,
        'title': 'Open Account'
    }
        
    return render(request, 'agent/efloat_account.html', context)

@login_required
@user_passes_test(is_agent)
def view_e_float_account(request):
    agent = request.user.agent
    today = timezone.now().date()
    
    account = get_object_or_404(EFloatAccount, agent=agent, date=today)
    
    # Notify the Owner if there is a surplus or shortage
    difference = Decimal(account.difference)
    if difference > 0:
        messages.warning(request, f"Surplus of GH¢{difference}. Please review the account.")
    elif difference < 0:
        messages.error(request, f"Shortage of GH¢{abs(difference)}. Please review the account.")
    
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
@login_required
@user_passes_test(is_agent)
def agent_dashboard(request):
    agent = request.user.agent
    agent_id = request.user
    today = timezone.now().date()
    total_cashins = CustomerCashIn.total_cash_for_customer(agent=agent_id, date_deposited=today)
    total_cashouts = CustomerCashOut.total_cashout_for_customer(agent=agent_id, date_withdrawn=today)
    total_deposits = BankDeposit.total_bank_deposit_for_customer(agent=agent, date_deposited=today)
    total_withdrawals = BankWithdrawal.total_bank_withdrawal_for_customer(agent=agent, date_withdrawn=today)
    total_ecash = CashAndECashRequest.total_ecash_for_customer(agent=agent, created_at=today)
    total_payments = PaymentRequest.total_payment_for_customer(agent=agent, created_at=today)
    customers = Customer.objects.filter(agent=agent)
    context = {
        'total_cashins': total_cashins,
        'total_cashouts': total_cashouts,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_ecash': total_ecash,
        'total_payments': total_payments,
        'customers': customers,
        'title': 'Dashboard'
    }
    return render(request, 'agent/dashboard.html', context)


def payto(request):
    agent = request.user
    if request.method == 'POST':
        agent_number = request.POST.get('agent_number')
        network = request.POST.get('network')
        deposit_type = request.POST.get('deposit_type')
        sent_to_agent_number = request.POST.get('sent_to_agent_number')
        merchant_code = request.POST.get('merchant_code')
        merchant_number = request.POST.get('merchant_number')
        amount = request.POST.get('amount')
        reference = request.POST.get('reference')
        
        paytos = CustomerPayTo(agent_number=agent_number, network=network, deposit_type=deposit_type, sent_to_agent_number=sent_to_agent_number, merchant_code=merchant_code, merchant_number=merchant_number, amount=amount, reference=reference)
        
        paytos.agent = agent
        
        paytos.save()
        
        return redirect('payto_notifications')
        
    context = {
        'title': 'Payto'
    }
    return render(request, 'agent/payto/payto.html', context)

@login_required
@user_passes_test(is_agent)
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
        cash_received = request.POST.get('cash_received')
        action = request.POST.get('action')  # 'proceed' or 'cancel'
        
        amount = Decimal(amount)
        cash_received = Decimal(cash_received)

        if CustomerFraud.objects.filter(customer_phone=customer_phone).exists():
            if action == 'proceed':
                cash_in = CustomerCashIn.objects.create(
                    agent=request.user, 
                    network=network, 
                    customer_phone=customer_phone, 
                    deposit_type=deposit_type, 
                    depositor_name=depositor_name, 
                    depositor_number=depositor_number, 
                    amount=amount, 
                    cash_received=cash_received,
                    is_fraudster=True,
                )
        
                messages.warning(request, 'Transaction completed with a flagged fraudster!')
                return render(request, 'agent/cashIn.html', {
                    'is_fraudster': True,
                    'network':network, 
                    'customer_phone':customer_phone, 
                    'deposit_type':deposit_type, 
                    'depositor_name':depositor_name, 
                    'depositor_number':depositor_number, 
                    'amount':amount, 
                    'cash_received':cash_received
                })
            elif action == 'cancel':
                messages.info(request, 'Transaction canceled due to fraudster alert.')
                return redirect('cashIn')
            
        cash_in = CustomerCashIn.objects.create(
            agent=request.user, 
            network=network, 
            customer_phone=customer_phone, 
            deposit_type=deposit_type, 
            depositor_name=depositor_name, 
            depositor_number=depositor_number, 
            amount=amount, 
            cash_received=cash_received
        )

        network_balance = getattr(account, f"{cash_in.network.lower()}_balance")
        get_amount = Decimal(cash_in.amount)
        if get_amount > Decimal(network_balance):
            messages.error(request, f"Insufficient balance in {cash_in.network}. Kindly make a request.")
            return redirect('cashIn')
    
        account.update_balance_for_cash_in(cash_in.network, cash_in.amount)
        messages.success(request, 'Customer Cash-In recorded succussfully.')
        return redirect('cashin_notifications')
    context = {
        'title': 'Cash In',
    }
    return render(request, 'agent/cashIn.html', context)


@login_required
@user_passes_test(is_agent)
def cashOut(request):
    agent = request.user.agent
    today = timezone.now().date()
    
    
    account = get_object_or_404(EFloatAccount, agent=agent, date=today)
    
    if request.method == 'POST':
        network = request.POST.get('network')
        customer_phone = request.POST.get('customer_phone')
        amount = request.POST.get('amount')
        cash_paid = request.POST.get('cash_paid')
        
        amount = Decimal(amount)
        cash_paid = Decimal(cash_paid)
        
        cash_out = CustomerCashOut(network=network, customer_phone=customer_phone, amount=amount, cash_paid=cash_paid)
        
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
        return redirect('cashout_notifications')
    context = {
        'title': 'Cash Out'
    }
    return render(request, 'agent/cashOut.html', context)

# Bank Deposit

def get_banks(request):
    phone_number = request.GET.get('phone_number')
    customers = CustomerAccount.objects.filter(phone_number=phone_number).values('bank').distinct()
    banks = [customer['bank'] for customer in customers]
    return JsonResponse(banks, safe=False)

def get_accounts(request):
    phone_number = request.GET.get('phone_number')
    bank = request.GET.get('bank')
    customers = CustomerAccount.objects.filter(phone_number=phone_number, bank=bank).values('account_number')
    accounts = [customer['account_number'] for customer in customers]
    return JsonResponse(accounts, safe=False)

def get_customer_details(request):
    account_number = request.GET.get('account_number')
    customer = get_object_or_404(CustomerAccount, account_number=account_number)
    data = {
        'account_name': customer.account_name
    }
    return JsonResponse(data)
    


@login_required
@user_passes_test(is_agent)
def agencyBank(request):
    agent = request.user.agent
    today = timezone.now().date()
    
    account = get_object_or_404(EFloatAccount, agent=agent, date=today)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        bank = request.POST.get('bank')
        account_number = request.POST.get('account_number')
        account_name = request.POST.get('account_name')
        amount = request.POST.get('amount')
        
        bank_deposit = BankDeposit(phone_number=phone_number, bank=bank, account_number=account_number, account_name=account_name, amount=amount)
        
        bank_deposit.agent = agent
        
        bank_balance = getattr(account, f"{bank_deposit.bank.lower()}_balance")
        
        get_deposit = Decimal(bank_deposit.amount)
        
        
        if get_deposit > Decimal(bank_balance):
            messages.error(request, f'Insufficient balance in {bank_deposit.bank}.')
            return redirect('agencyBank')
        
        bank_deposit.save()
        account.update_balance_for_bank_deposit(bank_deposit.bank, bank_deposit.amount, bank_deposit.status)
        messages.success(request, 'Bank Deposit recorded succussfully.')
        return redirect('bank_deposit_notifications')
    
    context = {
        'title': 'Bank Deposit',
    }
        
    return render(request, 'agent/agencyBank.html', context)

@login_required
@user_passes_test(is_agent)
def view_bank_deposits(request):
    agent = request.user.agent
    bank_deposits = BankDeposit.objects.filter(agent=agent).order_by('-date_deposited', '-time_deposited')
    context = {
        'bank_deposits': bank_deposits,
        'title': 'Bank Deposits'
    }
    return render(request, 'agent/financial_services/view_bank_deposits.html', context)

@login_required
@user_passes_test(is_agent)
def withdrawal(request):
    agent = request.user.agent
    today = timezone.now().date()
    
    account = get_object_or_404(EFloatAccount, agent=agent, date=today)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        bank = request.POST.get('bank')
        account_number = request.POST.get('account_number')
        account_name = request.POST.get('account_name')
        amount = request.POST.get('amount')
        
        bank_withdrawal = BankWithdrawal(customer_phone=phone_number, bank=bank, account_number=account_number, account_name=account_name, amount=amount)
        
        bank_withdrawal.agent = agent
        
        bank_balance = getattr(account, f"{bank_withdrawal.bank.lower()}_balance")
        
        get_withdrawal = Decimal(bank_withdrawal.amount)
        
        
        if get_withdrawal > Decimal(bank_balance):
            messages.error(request, f'Insufficient balance in {bank_withdrawal.bank}.')
            return redirect('withdrawal')
        
        bank_withdrawal.save()
        account.update_balance_for_bank_withdrawal(bank_withdrawal.bank, bank_withdrawal.amount, bank_withdrawal.status)
        messages.success(request, 'Bank Withdrawal recorded succussfully.')
        return redirect('bank_withdrawal_notifications')
    
    context = {
        'title': 'Bank Withdrawal',
    }
    
    return render(request, 'agent/withdrawal.html', context)

@login_required
@user_passes_test(is_agent)
def view_bank_withdrawals(request):
    agent = request.user.agent
    bank_withdrawals = BankWithdrawal.objects.filter(agent=agent).order_by('-date_withdrawn', '-time_withdrawn')
    context = {
        'bank_withdrawals': bank_withdrawals,
        'title': 'Bank Withdrawals'
    }
    return render(request, 'agent/financial_services/view_bank_withdrawals.html', context)

# Transaction summaries start----------
@login_required
@user_passes_test(is_agent)
def TotalTransactionSum(request):
    agent = request.user.agent
    agent_id = request.user
    today = timezone.now().date()
    
    total_cashins = CustomerCashIn.total_cash_for_customer(agent=agent_id, date_deposited=today)
    total_cashouts = CustomerCashOut.total_cashout_for_customer(agent=agent_id, date_withdrawn=today)
    total_deposits = BankDeposit.total_bank_deposit_for_customer(agent=agent, date_deposited=today)
    total_withdrawals = BankWithdrawal.total_bank_withdrawal_for_customer(agent=agent, date_withdrawn=today)
    total_ecash = CashAndECashRequest.total_ecash_for_customer(agent=agent, created_at=today)
    total_payments = PaymentRequest.total_payment_for_customer(agent=agent, created_at=today)
    
    context = {
        'total_cashins': total_cashins,
        'total_cashouts': total_cashouts,
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_ecash': total_ecash,
        'total_payments': total_payments,
        'title': 'Transaction Summary'

    }
    return render(request, 'agent/transaction_summary/TotalTransactionSum.html', context)

@login_required
def cashin_summary_date(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Set default date range (last 30 days)
    if not start_date and not end_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
     # Convert start_date and end_date to date objects if they are strings
    if start_date and isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date and isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    dates = CustomerCashIn.objects.values('date_deposited').annotate(total_amount=Sum('amount'))
    
    if start_date:
        dates = dates.filter(date_deposited__gte=start_date)
    if end_date:
        dates = dates.filter(date_deposited__lte=end_date)
        
    paginator = Paginator(dates, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'dates': dates,
        'start_date': start_date,
        'end_date': end_date,
        'title': 'Cash in Summary'
    }
    return render(request, 'agent/transaction_summary/cashin_summary_date.html', context)

@login_required
@user_passes_test(is_agent)
def cashin_summary(request, date):
    agent = request.user
    cashins = CustomerCashIn.objects.filter(agent=agent, date_deposited=date).order_by('-date_deposited', '-time_deposited')
    context = {
        'date': date,
        'cashins': cashins,
        'title': 'Cash In Summary'
    }
    return render(request, 'agent/transaction_summary/cashin_summary.html', context)


@login_required
def cashout_summary_date(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Set default date range (last 30 days)
    if not start_date and not end_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
     # Convert start_date and end_date to date objects if they are strings
    if start_date and isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date and isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
    dates = CustomerCashOut.objects.values('date_withdrawn').annotate(total_amount=Sum('amount'))
    
    if start_date:
        dates = dates.filter(date_withdrawn__gte=start_date)
    if end_date:
        dates = dates.filter(date_withdrawn__lte=end_date)
        
    paginator = Paginator(dates, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'dates': dates,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'agent/transaction_summary/cashout_summary_date.html', context)


@login_required
@user_passes_test(is_agent)
def cashout_summary(request, date):
    agent = request.user
    cashouts = CustomerCashOut.objects.filter(agent=agent, date_withdrawn=date).order_by('-date_withdrawn', '-time_withdrawn')
    context = {
        'date': date,
        'cashouts': cashouts,
        'title': 'Cash Out Summary'
    }
    return render(request, 'agent/transaction_summary/cashout_summary.html', context)


@login_required
def bank_deposit_summary_date(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Set default date range (last 30 days)
    if not start_date and not end_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
     # Convert start_date and end_date to date objects if they are strings
    if start_date and isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date and isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    dates = BankDeposit.objects.values('date_deposited').annotate(total_amount=Sum('amount'))
    if start_date:
        dates = dates.filter(date_deposited__gte=start_date)
    if end_date:
        dates = dates.filter(date_deposited__lte=end_date)
        
    paginator = Paginator(dates, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'dates': dates,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'agent/transaction_summary/bank_deposit_summary_date.html', context)


@login_required
@user_passes_test(is_agent)
def bank_deposit_summary(request, date):
    agent = request.user.agent
    bank_deposits = BankDeposit.objects.filter(agent=agent, date_deposited=date).order_by('-date_deposited', '-time_deposited')
    context = {
        'date': date,
        'bank_deposits': bank_deposits,
        'title': 'Bank Deposits Summary'
    }
    return render(request, 'agent/transaction_summary/bank_deposit_summary.html', context)


@login_required
def bank_withdrawal_summary_date(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Set default date range (last 30 days)
    if not start_date and not end_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
     # Convert start_date and end_date to date objects if they are strings
    if start_date and isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date and isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    dates = BankWithdrawal.objects.values('date_withdrawn').annotate(total_amount=Sum('amount'))
    if start_date:
        dates = dates.filter(date_withdrawn__gte=start_date)
    if end_date:
        dates = dates.filter(date_withdrawn__lte=end_date)
        
    paginator = Paginator(dates, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'dates': dates,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'agent/transaction_summary/bank_withdrawal_summary_date.html', context)


@login_required
@user_passes_test(is_agent)
def bank_withdrawal_summary(request, date):
    agent = request.user.agent
    bank_withdrawals = BankWithdrawal.objects.filter(agent=agent, date_withdrawn=date).order_by('-date_withdrawn', '-time_withdrawn')
    context = {
        'date': date,
        'bank_withdrawals': bank_withdrawals,
        'title': 'Bank Withdrawals Summary'
    }
    return render(request, 'agent/transaction_summary/bank_withdrawal_summary.html', context)


@login_required
def cash_summary_date(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Set default date range (last 30 days)
    if not start_date and not end_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
     # Convert start_date and end_date to date objects if they are strings
    if start_date and isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date and isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    dates = CashAndECashRequest.objects.values('created_at').annotate(total_amount=Sum('amount'))
    if start_date:
        dates = dates.filter(created_at__gte=start_date)
    if end_date:
        dates = dates.filter(created_at__lte=end_date)
        
    paginator = Paginator(dates, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'dates': dates,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'agent/transaction_summary/cash_summary_date.html', context)



@login_required
@user_passes_test(is_agent)
def cash_summary(request, date):
    agent = request.user.agent
    cash_requests = CashAndECashRequest.objects.filter(agent=agent, created_at=date).order_by('-created_at')
    context = {
        'date': date,
        'cash_requests': cash_requests,
        'title': 'Cash Summary'
    }
    return render(request, 'agent/transaction_summary/cash_summary.html', context)


@login_required
def payment_summary_date(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Set default date range (last 30 days)
    if not start_date and not end_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
     # Convert start_date and end_date to date objects if they are strings
    if start_date and isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date and isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    dates = PaymentRequest.objects.values('created_at').annotate(total_amount=Sum('amount'))
    if start_date:
        dates = dates.filter(created_at__gte=start_date)
    if end_date:
        dates = dates.filter(created_at__lte=end_date)
        
    paginator = Paginator(dates, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'dates': dates,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'agent/transaction_summary/payment_summary_date.html', context)



@login_required
@user_passes_test(is_agent)
def payment_summary(request, date):
    agent = request.user.agent
    payments = PaymentRequest.objects.filter(agent=agent, created_at=date).order_by('-created_at')
    context = {
        'date': date,
        'payments': payments,
        'title': 'Payments Summury'
    }
    return render(request, 'agent/transaction_summary/payment_summary.html', context)

# Transaction summaries end-------------
@login_required
@user_passes_test(is_agent)
def PaymentSummary(request):
    return render(request, 'agent/PaymentSummary.html')



@login_required
@user_passes_test(is_agent)
def my_customers(request):
    agent = request.user.agent
    customers = Customer.objects.filter(agent=agent)
    context = {
        'customers': customers,
        'title': 'My Customers'
    }
    return render(request, 'agent/my_customers.html', context)

def my_customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    accounts = customer.accounts.all()
    context = {
        'customer': customer,
        'accounts': accounts,
        'title': 'Customer Detail'
    }
    return render(request, 'agent/my_customer_detail.html', context)

@login_required
@user_passes_test(is_agent)
def customerReg(request):
    # users = User.objects.filter(role='CUSTOMER')
    branches = Branch.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        branch_id = request.POST.get('branch')
        phone_number = request.POST.get('phone_number')
        full_name = request.POST.get('full_name')
        customer_location = request.POST.get('customer_location')
        digital_address = request.POST.get('digital_address')
        id_type = request.POST.get('id_type')
        id_number = request.POST.get('id_number')
        date_of_birth = request.POST.get('date_of_birth')
        customer_picture = request.FILES.get('customer_picture')
        password = request.POST.get('password')
        
        # Validate required fields
        if not (username and password and phone_number and full_name and branch_id):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('customerReg')
        
        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('customerReg')
        
        # Check if the phone number already exists
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number already registered.')
            return redirect('customerReg')
        
        # Create the user
        user = User.objects.create(
            username=username,
            password=make_password(password),  # Hash the password
            phone_number=phone_number,
            role='CUSTOMER',
            is_approved=True  # Automatically approve customers
        )
        
        # user = get_object_or_404(User, id=customer_id)
        branch = get_object_or_404(Branch, id=branch_id)
        
        # Save the customer picture
        if customer_picture:
            picture_path = default_storage.save(f'customer_pic/{customer_picture.name}', customer_picture)
        else:
            picture_path = ''
            
        # agent = Agent.objects.get(user=request.user)
        
        # Create the customer
        Customer.objects.create(
            user=user,
            agent=request.user.agent,  # Assign the current agent
            branch=branch,
            phone_number=phone_number,
            full_name=full_name,
            customer_location=customer_location,
            digital_address=digital_address,
            id_type=id_type,
            id_number=id_number,
            date_of_birth=date_of_birth,
            customer_picture=picture_path
        )
        messages.success(request, 'Customer registered successfully!')
        return redirect('customerReg')

    context = {
        # 'users': users,
        'branches': branches,
        'title': 'Customer Registration'
    }
    return render(request, 'agent/customerReg.html', context)

@login_required
@user_passes_test(is_agent)
def accountReg(request):
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        account_number = request.POST['account_number']
        account_name = request.POST['account_name']
        bank = request.POST['bank']

        
        customer_accounts = CustomerAccount(account_number=account_number, account_name=account_name, bank=bank, phone_number=phone_number)
        
        try:
            customer = Customer.objects.get(phone_number=phone_number)
            customer_accounts.customer = customer
            customer_accounts.save()
            return redirect('accountReg')
        except Customer.DoesNotExist:
            messages.error(request, 'Customer with this phone number does not exist.')
        
    context = {
        'title': 'Account Registration'
    }
    return render(request, 'agent/accountReg.html', context)


@login_required
@user_passes_test(is_agent)
def payment(request):
    agent = request.user.agent
    today = timezone.now().date()
    
    account = get_object_or_404(EFloatAccount, agent=agent, date=today)
    
    if request.method == 'POST':
        mode_of_payment = request.POST.get('mode_of_payment')
        bank = request.POST.get('bank')
        network = request.POST.get('network')
        branch = request.POST.get('branch')
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        
        payments = PaymentRequest(mode_of_payment=mode_of_payment, bank=bank, network=network, branch=branch, name=name, amount=amount)
        payments.agent = agent
        
        
        # bank_balance = getattr(account, f"{payments.bank.lower()}_balance")
        # network_balance = getattr(account, f"{payments.network.lower()}_balance")
       
        # get_payment = Decimal(payments.amount)
        


        # if get_payment > Decimal(bank_balance):
        #     messages.error(request, f'Insufficient balance in {payments.bank}.')
        #     return redirect('payment')
        
        # elif get_payment > Decimal(network_balance):
        #     messages.error(request, f'Insufficient balance in {payments.network}.')
        #     return redirect('payment')
        
        
        payments.save()
        account.update_balance_for_payments(payments.bank, payments.network, payments.amount, payments.status)

        return redirect('payment_notifications')

    context = {
        'title': 'Payment Requests'
    }
    return render(request, 'agent/payment.html', context)

@login_required
@user_passes_test(is_agent)
def view_payments(request):
    agent = request.user.agent
    payments = PaymentRequest.objects.filter(agent=agent).order_by('-created_at')
    context = {
        'payments': payments,
        'title': 'Payments'
    }
    return render(request, 'agent/view_payments.html', context)

@login_required
@user_passes_test(is_agent)
def cashFloatRequest(request):
    agent = request.user.agent
    today = timezone.now().date()
    account = get_object_or_404(EFloatAccount, agent=agent, date=today)
    
    if request.method == 'POST':
        float_type = request.POST.get('float_type')
        bank = request.POST.get('bank')
        network = request.POST.get('network')
        amount = request.POST.get('amount')
        
        floats = CashAndECashRequest(float_type=float_type, bank=bank, network=network, amount=amount)
        
        floats.agent = agent
        floats.save()
        account.update_balance_for_cash_and_ecash(floats.bank, floats.network, floats.amount, floats.status)
        messages.success(request, 'Request submitted successfully. Waiting for Owner approveal.')
        
        return redirect('cash_notifications')
    
    context = {
        'title': 'Cash & ECash Request'
    }
    
    return render(request, 'agent/cashFloatRequest.html', context)

@login_required
@user_passes_test(is_agent)
def customer_care(request):
    context = {
        'title': 'Customer Care'
    }
    return render(request, 'agent/customer_care/customer_care.html', context)

@login_required
@user_passes_test(is_agent)
def customer_complains(request):
    agent = request.user.agent
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        complains = CustomerComplain(title=title, content=content)
        complains.agent = agent
        complains.save()
        
        messages.success(request, 'Your complain has been submitted successfully.')
        
        return redirect('view_customer_complains')
    
    context = {
        'title': 'Complains'
    }
    return render(request, 'agent/customer_care/complains.html', context)


@login_required
@user_passes_test(is_agent)
def view_customer_complains(request):
    agent = request.user.agent
    
    complains = CustomerComplain.objects.filter(agent=agent).order_by('-date')
    
    context = {
        'complains': complains,
        'title': 'Complains'
    }
    return render(request, 'agent/customer_care/complains_view.html', context)


@login_required
@user_passes_test(is_agent)
def customer_hold_account(request):
    agent = request.user.agent
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        customer_phone = request.POST.get('customer_phone')
        agent_number = request.POST.get('agent_number')
        transaction_id = request.POST.get('transaction_id')
        reasons = request.POST.get('reasons')
        
        hold_accounts = HoldCustomerAccount(amount=amount, customer_phone=customer_phone, agent_number=agent_number, transaction_id=transaction_id, reasons=reasons)
        
        hold_accounts.agent = agent
        hold_accounts.save()
        return redirect('view_customer_hold_account')
    context = {
        'title': 'Hold Account'
    }
    return render(request, 'agent/customer_care/hold_account.html', context)


@login_required
@user_passes_test(is_agent)
def view_customer_hold_account(request):
    agent = request.user.agent
    
    hold_accounts = HoldCustomerAccount.objects.filter(agent=agent).order_by('-date')
    context = {
        'hold_accounts': hold_accounts,
        'title': 'Hold Account'
    }
    return render(request, 'agent/customer_care/hold_account_view.html', context)


@login_required
@user_passes_test(is_agent)
def customer_fraud(request):
    agent = request.user.agent
    if request.method == 'POST':
        customer_phone = request.POST.get('customer_phone')
        reasons = request.POST.get('reasons')
        
        frauds = CustomerFraud(customer_phone=customer_phone, reasons=reasons)
        frauds.agent = agent
        frauds.save()
        return redirect('view_customer_fraud')
    
    context = {
        'title': 'Fraud'
    }
    return render(request, 'agent/customer_care/fraud.html', context)


@login_required
@user_passes_test(is_agent)
def view_customer_fraud(request):
    agent = request.user.agent
    frauds = CustomerFraud.objects.filter(agent=agent).order_by('-date')
    context = {
        'frauds': frauds,
        'title': 'Fraud'
    }
    return render(request, 'agent/customer_care/fraud_views.html', context)

def calculate(request):
    agent = request.user.agent
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        phone_number = request.POST.get('phone_number')
        amount = request.POST.get('amount')
        d_200 = request.POST.get('d_200')
        d_100 = request.POST.get('d_100')
        d_50 = request.POST.get('d_50')
        d_20 = request.POST.get('d_20')
        d_10 = request.POST.get('d_10')
        d_5 = request.POST.get('d_5')
        d_2 = request.POST.get('d_2')
        d_1 = request.POST.get('d_1')
        
         # Create a new CustomerPaymentAtBank instance
        payment = CustomerPaymentAtBank(
            customer_name=customer_name,
            phone_number=phone_number,
            amount=amount,
            d_200=d_200,
            d_100=d_100,
            d_50=d_50,
            d_20=d_20,
            d_10=d_10,
            d_5=d_5,
            d_2=d_2,
            d_1=d_1
        )
        payment.agent = agent
        payment.save()
        return redirect('calculate')
    
    context = {
        'title': 'Customer Payment',
    }
    return render(request, 'agent/calculate.html', context)



# Notifications

def cashin_notifications(request):
    return render(request, 'agent/notifications/cashin_notifications.html')

def cashout_notifications(request):
    return render(request, 'agent/notifications/cashout_notifications.html')

def bank_deposit_notifications(request):
    return render(request, 'agent/notifications/bank_deposit_notifications.html')

def bank_withdrawal_notifications(request):
    return render(request, 'agent/notifications/bank_withdrawal_notifications.html')

def cash_notifications(request):
    return render(request, 'agent/notifications/cash_notifications.html')

def payment_notifications(request):
    return render(request, 'agent/notifications/payment_notifications.html')

def payto_notifications(request):
    return render(request, 'agent/notifications/payto_notifications.html')

def errorPage(request):
    return render(request, 'agent/errorPage.html')


def commission(request):
    filter_type = request.GET.get('filter', 'daily') # Default to daily
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    agent = Agent.objects.get(agent=request.user)
    
    if filter_type == 'daily':
        cashincommissions = CashInCommission.objects.filter(customer_cash_in__agent=request.user, date=datetime.today())
        cashoutcommissions = CashOutCommission.objects.filter(customer_cash_out__agent=request.user, date=datetime.today())
    elif filter_type == 'monthly':
        start_of_month = datetime.today().replace(day=1)
        cashincommissions = CashInCommission.objects.filter(customer_cash_in__agent=request.user, date__gte=start_of_month, date__lte=datetime.today())
        cashoutcommissions = CashOutCommission.objects.filter(customer_cash_out__agent=request.user, date__gte=start_of_month, date__lte=datetime.today())
    elif start_date and end_date:
        cashincommissions = CashInCommission.objects.filter(customer_cash_in__agent=request.user, date__gte=start_date, date__lte=end_date)
        cashoutcommissions = CashOutCommission.objects.filter(customer_cash_out__agent=request.user, date__gte=start_date, date__lte=end_date)
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
    return render(request, 'agent/commission.html', context)