from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import MobilizationPayTo, BankDeposit, BankWithdrawal, PaymentRequest, CustomerAccount, TellerCalculator
from django.contrib import messages
from users.models import MobilizationCustomer, User, Branch, Customer
from django.contrib.auth.hashers import make_password
from django.core.files.storage import default_storage
from django.db.models import Sum
from django.utils import timezone

def is_mobilization(user):
    return user.role == 'MOBILIZATION'
# Create your views here.

def mobilization_account(request):
    mobilization = request.user.mobilization
    today = timezone.now().date()
    total_deposits = BankDeposit.total_bank_deposit_for_customer(mobilization=mobilization, date_deposited=today)
    total_payments = PaymentRequest.total_payment_for_customer(mobilization=mobilization, created_at=today)
    balance_left = total_deposits - total_payments
    context = {
        'total_deposits': total_deposits,
        'total_payments': total_payments,
        'balance_left': balance_left,
        'title': 'Account'
    }
    return render(request, 'mobilization/account.html', context)

@login_required
@user_passes_test(is_mobilization)
def dashboard(request):
    mobilization = request.user.mobilization
    today = timezone.now().date()
    customers = MobilizationCustomer.objects.filter(mobilization=mobilization)
    total_deposits = BankDeposit.total_bank_deposit_for_customer(mobilization=mobilization, date_deposited=today)
    total_withdrawals = BankWithdrawal.total_bank_withdrawal_for_customer(mobilization=mobilization, date_withdrawn=today)
    total_payments = PaymentRequest.total_payment_for_customer(mobilization=mobilization, created_at=today)
    context = {
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_payments': total_payments,
        'customers': customers,
        'title': 'Dashboard'
    }
    return render(request, 'mobilization/dashboard.html', context)

@login_required
@user_passes_test(is_mobilization)
def payto(request):
    mobilization = request.user
    if request.method == 'POST':
        agent_number = request.POST.get('agent_number')
        network = request.POST.get('network')
        deposit_type = request.POST.get('deposit_type')
        sent_to_agent_number = request.POST.get('sent_to_agent_number')
        merchant_code = request.POST.get('merchant_code')
        merchant_number = request.POST.get('merchant_number')
        amount = request.POST.get('amount')
        reference = request.POST.get('reference')
        
        paytos = MobilizationPayTo(agent_number=agent_number, network=network, deposit_type=deposit_type, sent_to_agent_number=sent_to_agent_number, merchant_code=merchant_code, merchant_number=merchant_number, amount=amount, reference=reference)
        
        paytos.mobilization = mobilization
        
        paytos.save()
        
        return redirect('mobilization_payto_success')
        
    context = {
        'title': 'Payto'
    }
    return render(request, 'mobilization/payto.html', context)


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
@user_passes_test(is_mobilization)
def bank_deposit(request):
    
    mobilization = request.user.mobilization
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        bank = request.POST.get('bank')
        account_number = request.POST.get('account_number')
        account_name = request.POST.get('account_name')
        mobilization_transaction_id = request.POST.get('mobilization_transaction_id')
        amount = request.POST.get('amount')
        
        bank_deposit = BankDeposit(phone_number=phone_number, bank=bank, account_number=account_number, account_name=account_name, mobilization_transaction_id=mobilization_transaction_id, amount=amount)
        
        bank_deposit.mobilization = mobilization
        
        bank_deposit.save()
        
        return redirect('mobilization_bank_deposit_success')
    
    context = {
        'title': 'Bank Deposit'
    }
    return render(request, 'mobilization/bank_deposit.html', context)

@login_required
@user_passes_test(is_mobilization)
def bank_withdrawal(request):
    
    mobilization = request.user.mobilization
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        bank = request.POST.get('bank')
        account_number = request.POST.get('account_number')
        account_name = request.POST.get('account_name')
        amount = request.POST.get('amount')
        
        bank_withdrawals = BankWithdrawal(customer_phone=phone_number, bank=bank, account_number=account_number, account_name=account_name, amount=amount)
        
        bank_withdrawals.mobilization = mobilization
        
        bank_withdrawals.save()
        
        return redirect('mobilization_bank_withdrawal_success')
    
    context = {
        'title': 'Bank Withdrawal'
    }
    return render(request, 'mobilization/bank_withdrawal.html', context)


@login_required
@user_passes_test(is_mobilization)
def payment(request):
    mobilization = request.user.mobilization

    if request.method == 'POST':
        mode_of_payment = request.POST.get('mode_of_payment')
        bank = request.POST.get('bank')
        network = request.POST.get('network')
        branch = request.POST.get('branch')
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        mobilization_transaction_id = request.POST.get('mobilization_transaction_id')
        
        payments = PaymentRequest(mode_of_payment=mode_of_payment, bank=bank, network=network, branch=branch, name=name, amount=amount, mobilization_transaction_id=mobilization_transaction_id)
        payments.mobilization = mobilization
        
        
        payments.save()
        return redirect('mobilization_payment_success')
    context = {
        'title': 'Payment Requests'
    }
    return render(request, 'mobilization/payment.html', context)


@login_required
@user_passes_test(is_mobilization)
def customer_registration(request):
    # users = User.objects.filter(role='CUSTOMER')
    branches = Branch.objects.all()
    if request.method == 'POST':
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
        if not (phone_number and password and full_name and branch_id):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('mobilization_customer_registration')
        
        # Check if the username already exists
        # if User.objects.filter(username=username).exists():
        #     messages.error(request, 'Username already taken.')
        #     return redirect('mobilization_customer_registration')
        
        # Check if the phone number already exists
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number already registered.')
            return redirect('mobilization_customer_registration')
        
        # Create the user
        user = User.objects.create(
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
            customer=user,
            mobilization=request.user.mobilization,  # Assign the current agent
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
        return redirect('mobilization_customer_registration')

    context = {
        # 'users': users,
        'branches': branches,
        'title': 'Customer Registration'
    }

    return render(request, 'mobilization/customer_registration.html', context)

@login_required
@user_passes_test(is_mobilization)
def customer_account_registration(request):
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
            messages.success(request, 'Customer registered successfully!')
            return redirect('customer_account_registration')
        except Customer.DoesNotExist:
            messages.error(request, 'Customer with this phone number does not exist.')
        
    context = {
        'title': 'Account Registration'
    }
    return render(request, 'mobilization/customer_account_registration.html', context)

@login_required
@user_passes_test(is_mobilization)
def my_customers(request):
    mobilization = request.user.mobilization
    customers = Customer.objects.filter(mobilization=mobilization)
    context = {
        'customers': customers,
        'title': 'My Customers'
    }
    return render(request, 'mobilization/my_customers.html', context)

@login_required
@user_passes_test(is_mobilization)
def my_customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    accounts = customer.customeraccounts.all()
    context = {
        'customer': customer,
        'accounts': accounts,
        'title': 'Customer Detail'
    }
    return render(request, 'mobilization/my_customer_detail.html', context)

@login_required
@user_passes_test(is_mobilization)
def transaction_summary(request):
    
    mobilization = request.user.mobilization
    today = timezone.now().date()
    total_deposits = BankDeposit.total_bank_deposit_for_customer(mobilization=mobilization, date_deposited=today)
    total_withdrawals = BankWithdrawal.total_bank_withdrawal_for_customer(mobilization=mobilization, date_withdrawn=today)
    total_payments = PaymentRequest.total_payment_for_customer(mobilization=mobilization, created_at=today)
    
    context = {
        'total_deposits': total_deposits,
        'total_withdrawals': total_withdrawals,
        'total_payments': total_payments,
        'title': 'Transaction Summary'

    }
    return render(request, 'mobilization/transactions/transaction_summary.html', context)

@login_required
@user_passes_test(is_mobilization)
def bank_deposit_summary_date(request):
    dates = BankDeposit.objects.values('date_deposited').annotate(total_amount=Sum('amount'))
    context = {
        'dates': dates
    }
    return render(request, 'mobilization/transactions/bank_deposit_summary_date.html', context)


@login_required
@user_passes_test(is_mobilization)
def bank_deposit_summary(request, date):
    mobilization = request.user.mobilization
    bank_deposits = BankDeposit.objects.filter(mobilization=mobilization, date_deposited=date).order_by('-date_deposited', '-time_deposited')
    context = {
        'date': date,
        'bank_deposits': bank_deposits,
        'title': 'Bank Deposits Summary'
    }
    return render(request, 'mobilization/transactions/bank_deposit_summary.html', context)


@login_required
@user_passes_test(is_mobilization)
def bank_withdrawal_summary_date(request):
    dates = BankWithdrawal.objects.values('date_withdrawn').annotate(total_amount=Sum('amount'))
    context = {
        'dates': dates
    }
    return render(request, 'mobilization/transactions/bank_withdrawal_summary_date.html', context)


@login_required
@user_passes_test(is_mobilization)
def bank_withdrawal_summary(request, date):
    mobilization = request.user.mobilization
    bank_withdrawals = BankWithdrawal.objects.filter(mobilization=mobilization, date_withdrawn=date).order_by('-date_withdrawn', '-time_withdrawn')
    context = {
        'date': date,
        'bank_withdrawals': bank_withdrawals,
        'title': 'Bank Withdrawals Summary'
    }
    return render(request, 'mobilization/transactions/bank_withdrawal_summary.html', context)


@login_required
@user_passes_test(is_mobilization)
def payment_summary_date(request):
    dates = PaymentRequest.objects.values('created_at').annotate(total_amount=Sum('amount'))
    context = {
        'dates': dates
    }
    return render(request, 'mobilization/transactions/payment_summary_date.html', context)


@login_required
@user_passes_test(is_mobilization)
def payment_summary(request, date):
    mobilization = request.user.mobilization
    payments = PaymentRequest.objects.filter(mobilization=mobilization, created_at=date).order_by('-created_at')
    context = {
        'date': date,
        'payments': payments,
        'title': 'Payments Summury'
    }
    return render(request, 'mobilization/transactions/payment_summary.html', context)

@login_required
@user_passes_test(is_mobilization)
def calculator(request):
    mobilization = request.user.mobilization
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
        payment = TellerCalculator(
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
        payment.mobilization = mobilization
        payment.save()
        return redirect('mobilization_calculator')
    context = {
        'title': 'Calculator'
    }
    return render(request, 'mobilization/calculator.html', context)

@login_required
@user_passes_test(is_mobilization)
def view_calculator(request):
    mobilization = request.user.mobilization
    calculators = TellerCalculator.objects.filter(mobilization=mobilization)
    context = {
        'calculators': calculators,
        'title': 'View Calculator'
    }
    return render(request, 'mobilization/view_calculators.html', context)


def bank_deposit_notifications(request):
    return render(request, 'mobilization/notifications/bank_deposit_notifications.html')

def bank_withdrawal_notifications(request):
    return render(request, 'mobilization/notifications/bank_withdrawal_notifications.html')

def payment_notifications(request):
    return render(request, 'mobilization/notifications/payment_notifications.html')

def payto_notifications(request):
    return render(request, 'mobilization/notifications/payto_notifications.html')