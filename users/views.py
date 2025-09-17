from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import auth
from django.contrib.auth.backends import ModelBackend

from accountant.models import Transaction, Vehicle
from accountant.models import Branch as branch
from accountant.forms import TransactionUpdateForm, MonthYearFilterForm
from agent.serializers import TransactionSerializer
from .forms import UserRegisterForm, OwnerRegistrationForm, DriverRegistrationForm, CustomPasswordChangeForm, CustomerFilterForm, AccountFilterForm, AccountantRegistrationForm, AgentRegistrationForm, CustomerRegistrationForm, LoginForm, MobilizationRegistrationForm
from .models import User, Owner, Agent, Customer, Branch, Mobilization, OTPToken, Driver, Accountant
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from .utils import send_otp, send_otp_via_email, generate_otp, send_otp_sms, send_reset_password_otp_sms
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import time

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import LoginSerializer, UserSerializer

from driver.models import MileageRecord, FuelRecord, Expense
from django.db.models import F
from driver.forms import MileageRecordForm, FuelRecordForm, ExpenseForm
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce


from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView


from mobilization.models import CustomerAccount


def all_requests(request):
    return render(request, 'users/admin_dashboard/request.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # Deactivate account until OTP is verified
            user.save()
            # Generate OTP and store it in session
            otp = generate_otp()
            request.session['registration_otp'] = otp
            request.session['registration_user_id'] = user.id
            send_otp_sms(user.phone_number, otp)
            messages.success(request, 'Registration succss.')
            return redirect('verify_registration_otp')
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserRegisterForm()
        
    context = {
        'form': form
    }
    return render(request, 'users/register.html', context)


def verify_registration_otp(request):
    if request.method == 'POST':
        input_otp = request.POST.get('otp')
        session_otp = request.session.get('registration_otp')
        user_id = request.session.get('registration_user_id')
        
        if input_otp and session_otp and input_otp == session_otp:
            # OTP is correct. Activate the user and log them in.
            user = get_object_or_404(User, id=user_id)
            user.is_active = True
            user.save()
            
            # Clean up session data
            del request.session['registration_otp']
            del request.session['registration_user_id']
            
            messages.success(request, "Registration completed! You are now logged in.")
            return redirect("login")
            
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            
    return render(request, 'users/verify_registration_otp.html')


def login_user(request):
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            messages.error(request, 'Phone number is not registered')
            return redirect('login')
        
        user = authenticate(request, phone_number=phone_number, password=password)
        
        
        if user is not None:
            if user.is_otp_verified_today():
                login(request, user)
                if user.is_approved and not user.is_blocked:
                    if user.role == "ADMIN":
                        return redirect("admin_dashboard")
                    elif user.role == "OWNER":
                        return redirect("owner-dashboard")
                    elif user.role == "BRANCH":
                        return redirect("agent-dashboard")
                    elif user.role == "MOBILIZATION":
                        return redirect("mobilization_dashboard")
                    elif user.role == "DRIVER":
                        return redirect("driver_dashboard")
                    elif user.role == "ACCOUNTANT":
                        return redirect("accountant_dashboard")
                elif user.is_blocked:
                    messages.error(request, "Your account has been blocked. Please contact the admin.")
                    return redirect('login')
                else:
                    messages.error(request, "Your account is not yet approved by the admin.")
                    return redirect('login')
            else:
                user.generate_otp()
                send_otp(user.phone_number, user.otp)
                request.session['phone_number'] = phone_number  # Store phone number in session
                send_otp_via_email(user.email, user.otp)
                return redirect('verify_otp')
        else:
            messages.error(request, 'Invalid password.')
            return redirect('login')

        
    context = {
      
        'title': 'Login'
    }
    
    return render(request, 'users/login.html', context)

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        phone_number = request.session.get('phone_number')

        if phone_number:
            user = User.objects.get(phone_number=phone_number)
            if user.is_otp_valid(otp):
                user.otp_verified_at = timezone.now()
                user.save()
                backend = 'django.contrib.auth.backends.ModelBackend'  # Default backend
                login(request, user, backend=backend)
                if user.is_approved and not user.is_blocked:
                    if user.role == "ADMIN":
                        return redirect("admin_dashboard")
                    elif user.role == "OWNER":
                        return redirect("owner-dashboard")
                    elif user.role == "BRANCH":
                        return redirect("agent-dashboard")
                    elif user.role == "MOBILIZATION":
                        return redirect("mobilization_dashboard")
                    elif user.role == "ACCOUNTANT":
                        return redirect("accountant_dashboard")
                elif user.is_blocked:
                    messages.error(request, "Your account has been blocked. Please contact the admin.")
                else:
                    messages.error(request, "Your account is not yet approved by the admin.")
            else:
                messages.error(request, 'Invalid or expired OTP.')
        else:
            messages.error(request, 'Session expired. Please log in again.')
            return redirect('login')
        
    context = {
      
        'title': 'Verify OTP'
    }
    
    return render(request, 'users/verify_otp.html', context)

def resend_otp(request):
    phone_number = request.session.get('phone_number')
    if phone_number:
        user = User.objects.get(phone_number=phone_number)
        user.generate_otp()  # Generate a new OTP
        send_otp(user.phone_number, user.otp)  # Send the new OTP
        send_otp_via_email(user.email, user.otp)
        messages.success(request, 'A new OTP has been sent to your phone number or email.')
    else:
        messages.error(request, 'Session expired. Please register again.')
    return redirect('verify_otp')


def send_reset_otp(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            messages.error(request, 'No account found with this phone number')
            return redirect('password_reset')
        
        otp_token = OTPToken.objects.create(
            user=user,
            phone_number=phone_number
        )
        
        try:
            send_reset_password_otp_sms(phone_number, otp_token.otp)
            messages.success(request, 'OTP sent to your phone number')
            request.session['otp_user_id'] = user.id
            return redirect('verify_reset_otp')
        except Exception as e:
            messages.error(request, f'Failed to send OTP: {str(e)}')
            return redirect('send_reset_otp')
        
    return render(request, 'users/send_reset_otp.html')


def verify_reset_otp(request):
    if 'otp_user_id' not in request.session:
        return redirect('send_reset_otp')
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        user_id = request.session['otp_user_id']
    
        try:
            otp_token = OTPToken.objects.get(
                user_id=user_id,
                otp=otp,
                is_verified=False,
                expires_at__gt=timezone.now()
            )
            otp_token.is_verified = True
            otp_token.save()
            request.session['otp_verified'] = True
            messages.success(request, 'OTP verified successfully')
            return redirect('change_password')
        except OTPToken.DoesNotExist:
            messages.error(request, 'Invalid or expired OTP')
    
    return render(request, 'users/verified_reset_otp.html')


def change_password(request):
    if 'otp_verified' not in request.session or not request.session['otp_verified']:
        return redirect('send_reset_otp')
    
    if request.method == 'POST':
        user_id = request.session['otp_user_id']
        user = User.objects.get(id=user_id)
        form = CustomPasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            del request.session['otp_verified']
            del request.session['otp_user_id']
            messages.success(request, 'Your password was successfully updated!')
            return redirect('login')
    else:
        user_id = request.session['otp_user_id']
        user = User.objects.get(id=user_id)
        form = CustomPasswordChangeForm(user)
        
    context = {
        'form': form
    }
        
    return render(request, 'users/change_password.html', context)
            


def logout(request):
    
    auth.logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('login')

# Role Check Functions
def is_admin(user):
    return user.role == 'ADMIN'

def is_owner(user):
    return user.role == 'OWNER'

def is_agent(user):
    return user.role == 'BRANCH'

def is_mobilization(user):
    return user.role == 'MOBILIZATION'

def is_driver(user):
    return user.role == 'DRIVER'

def is_accountant(user):
    return user.role == 'ACCOUNTANT'

# Admin Dashboard
def admin_dashboard(request):
    # Fetch all users, owners, agents, and customers
    unapproved_users = User.objects.filter(is_approved=False)
    unapproved_users_count = User.objects.filter(is_approved=False).count()

    
    context = {
        'unapproved_users': unapproved_users,
        'unapproved_users_count': unapproved_users_count,
        'title': 'Admin Dashboard',

    }
    return render(request, 'users/admin_dashboard/dashboard.html', context)

def unapproved_users_count(request):
    unapproved_users_count = User.objects.filter(is_approved=False).count()
    context = {
        'unapproved_users_count': unapproved_users_count,
    }
    return context

# def get_users(request):
#     users = Owner.objects.filter(user=request.user)
#     return {'users': users}


@login_required
@user_passes_test(is_admin)
def approve_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_approved = True
    user.save()
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def unapprove_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_approved = False
    user.save()
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
def block_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_blocked = True # Toggle block status
    user.save()
    return redirect('admin_dashboard')


@login_required
@user_passes_test(is_admin)
def unblock_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_blocked = False
    user.save()
    return redirect('admin_dashboard')

def delete_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect("admin_dashboard")


def PaymentRequest(request):
    return render(request, 'users/admin_dashboard/PaymentRequest.html')

def unpaidRequest(request):
    return render(request, 'users/admin_dashboard/unpaidRequest.html')

@login_required
@user_passes_test(is_admin)
def register_owner(request):
    if request.method == 'POST':
        form = OwnerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = OwnerRegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'users/admin_dashboard/register_owner.html', context)

def my_owners(request):
    my_owners = Owner.objects.all()
    context = {
        'my_owners': my_owners,
        'title': 'My Owners'
    }
    return render(request, 'users/admin_dashboard/my_owners.html', context)

def balance(request):
    return render(request, 'users/admin_dashboard/balance.html')

def all_users(request):
    # Fetch all users, owners, agents, and customers
    admins = User.objects.filter(role="ADMIN")
    agents = User.objects.filter(role="BRANCH")
    owners = User.objects.filter(role="OWNER")
    mobilizations = User.objects.filter(role="MOBILIZATION")
    drivers = User.objects.filter(role="DRIVER")
    customers = User.objects.filter(role="CUSTOMER")
    accountants = User.objects.filter(role="ACCOUNTANT")
    
    context = {
        'admins': admins,
        'owners': owners,
        'agents': agents,
        'mobilizations': mobilizations,
        'drivers': drivers,
        'customers': customers,
        'accountants': accountants,
        'title': 'Users'

    }
    return render(request, 'users/admin_dashboard/users.html', context)

def birthdays(request):
    upcoming_customers = Customer.upcoming_birthdays(days=5)
    
    # Annotate each customer with days until birthday
    customers_with_days = [
        {
            'customer': customer,
            'days_until': customer.days_until_birthday,
            'birthday_date': customer.date_of_birth.strftime('%b %d')  # Format as "Jun 15"
        }
        for customer in upcoming_customers
    ]
    
    # Sort by days until birthday (soonest first)
    customers_with_days.sort(key=lambda x: x['days_until'])
    
    context = {
        'upcoming_birthdays': customers_with_days,
        'days_ahead': 5
    }
    return render(request, 'users/admin_dashboard/birthdays.html', context)


def register_driver(request):
    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('register-driver')
    else:
        form = DriverRegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'users/admin_dashboard/driver/register_driver.html', context)

def my_drivers(request):
    my_drivers = Driver.objects.all()
    context = {
        'my_drivers': my_drivers,
        'title': 'My Drivers',
    }
    return render(request, 'users/admin_dashboard/driver/my_drivers.html', context)


# Driver

def driver_detail(request, driver_id):
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    driver = get_object_or_404(Driver, id=driver_id)
    
     # Get driver's mileage with calculated mileage
    mileage_records = MileageRecord.objects.filter(
        driver=driver,
        date__month=current_month,
        date__year=current_year
    ).annotate(
        calculated_mileage=F('end_mileage') - F('start_mileage')
    )
    total_mileage = mileage_records.aggregate(
        total=Sum('calculated_mileage')
    )['total'] or 0
    
    # Get driver's fuel records for the current month
    fuel_records = FuelRecord.objects.filter(
        driver=driver,
        date__month=current_month,
        date__year=current_year
    )
    total_fuel = fuel_records.aggregate(total=Sum('amount'))['total'] or 0
    
    # Get driver's expenses for the current month
    expenses = Expense.objects.filter(
        driver=driver,
        date__month=current_month,
        date__year=current_year
    )
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'driver': driver,
        'mileage_records': mileage_records,
        'total_mileage': total_mileage,
        'fuel_records': fuel_records,
        'total_fuel': total_fuel,
        'expenses': expenses,
        'total_expenses': total_expenses,
    }
    
    return render(request, 'users/admin_dashboard/driver/details/driver_detail.html', context)

def customers(request):
    customers = Customer.objects.all()
    form = CustomerFilterForm(request.GET or None)
    if form.is_valid():
        if form.cleaned_data['phone_number']:
            customers = customers.filter(phone_number__icontains=form.cleaned_data['phone_number'])
        
    context = {
        'customers': customers,
        'form': form,
        'title': 'My Customers'
    }
    return render(request, 'users/admin_dashboard/customers.html', context)

def customer_accounts(request):
    accounts = CustomerAccount.objects.all()
    form = AccountFilterForm(request.GET or None)
    if form.is_valid():
        if form.cleaned_data['phone_number']:
            accounts = accounts.filter(phone_number__icontains=form.cleaned_data['phone_number'])
        
    context = {
        'accounts': accounts,
        'form': form,
        'title': 'My Customers'
    }
    return render(request, 'users/admin_dashboard/customer_accounts.html', context)

def my_customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    accounts = customer.customeraccounts.all()
    context = {
        'customer': customer,
        'accounts': accounts,
        'title': 'Customer Detail',
        'creator': customer.agent if customer.agent else customer.mobilization
    }

    return render(request, 'users/admin_dashboard/customer_detail.html', context)

def delete_account(request, account_id):
    account = CustomerAccount.objects.get(id=account_id)
    account.delete()
    return redirect("all-customer-accounts")

@login_required
@user_passes_test(is_admin)
def register_accountant(request):
    if request.method == 'POST':
        form = AccountantRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = AccountantRegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'users/admin_dashboard/accountant/register_accountant.html', context)

def my_accountants(request):
    # Get all available years with transactions
    available_years = Transaction.objects.dates('date', 'year').order_by('-date')
    
    # Get selected year/month from request
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    
    # Set defaults if not provided
    if not selected_year:
        selected_year = timezone.now().year
    if not selected_month:
        selected_month = timezone.now().month
    
    selected_year = int(selected_year)
    selected_month = int(selected_month)
        
     # Get all branches with their totals
    branches = branch.objects.annotate(
        total_income=Sum('transactions__amount',
                        filter=Q(transactions__transaction_type='income') &
                               Q(transactions__date__year=selected_year) &
                               Q(transactions__date__month=selected_month)),
        total_expense=Sum('transactions__amount',
                         filter=Q(transactions__transaction_type='expense') &
                                Q(transactions__date__year=selected_year) &
                                Q(transactions__date__month=selected_month))
    )
    
     # Get all vehicles with their totals
    vehicles = Vehicle.objects.annotate(
        vehicle_income=Sum('transactions__amount',
                          filter=Q(transactions__transaction_type='income') &
                                 Q(transactions__date__year=selected_year) &
                                 Q(transactions__date__month=selected_month)),
        vehicle_expense=Sum('transactions__amount',
                           filter=Q(transactions__transaction_type='expense') &
                                  Q(transactions__date__year=selected_year) &
                                  Q(transactions__date__month=selected_month))
    )
    
     # Calculate grand totals
    grand_total_income = sum(b.total_income or 0 for b in branches)
    grand_total_expense = sum(b.total_expense or 0 for b in branches)
    grand_total_balance = grand_total_income - grand_total_expense
    
    grand_vehicle_total_income = sum(b.vehicle_income or 0 for b in vehicles)
    grand_vehicle_total_expense = sum(b.vehicle_expense or 0 for b in vehicles)
    grand_vehicle_total_balance = grand_vehicle_total_income - grand_vehicle_total_expense
    
    months = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    
    

    
    context = {
        
        'months': months,
        'available_years': [d.year for d in available_years],
        'selected_year': selected_year,
        'selected_month': selected_month,
        
        'branches': branches,
        'vehicles': vehicles,
        'grand_total_income': grand_total_income,
        'grand_total_expense': grand_total_expense,
        'grand_total_balance': grand_total_balance,
        
        'grand_vehicle_total_income': grand_vehicle_total_income,
        'grand_vehicle_total_expense': grand_vehicle_total_expense,
        'grand_vehicle_total_balance': grand_vehicle_total_balance,
        
        
    }
    
    return render(request, 'users/admin_dashboard/accountant/my_accountant.html', context)

from django.db.models.functions import TruncMonth
from django.db.models import Sum
from collections import defaultdict

def all_transactions(request):
    form = MonthYearFilterForm(request.GET or None)
    transactions = Transaction.objects.all().order_by('-created_at')
    
    # Apply filters if form is valid
    if form.is_valid():
        month = form.cleaned_data.get('month')
        year = form.cleaned_data.get('year')
        vehicle = form.cleaned_data.get('vehicle')
        branch = form.cleaned_data.get('branch')
        
        if month:
            transactions = transactions.filter(date__month=month)
        if year:
            transactions = transactions.filter(date__year=year)
        if vehicle:
            transactions = transactions.filter(vehicle=vehicle)
        if branch:
            transactions = transactions.filter(branch=branch)
    
    # Monthly summary (unfiltered to show all months)
    monthly_summary = Transaction.objects.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total_income=Sum('amount', filter=Q(transaction_type='income')),
        total_expense=Sum('amount', filter=Q(transaction_type='expense')),
    ).order_by('-month')
    
    # Group transactions by month for display
    monthly_transactions = defaultdict(list)
    for transaction in transactions:
        month_year = transaction.date.strftime("%B %Y")
        monthly_transactions[month_year].append(transaction)
        
     # Calculate totals for the filtered results
    total_income = transactions.filter(transaction_type='income').aggregate(
        Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(
        Sum('amount'))['amount__sum'] or 0
    net_balance = total_income - total_expense
    
    context = {
        'form': form,
        'transactions': transactions,
        'monthly_summary': monthly_summary,
        'monthly_transactions': dict(monthly_transactions),
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
    }
    
    return render(request, 'users/admin_dashboard/accountant/all_transactions.html', context)

def accountant_detail(request, accountant_id):
    accountant = get_object_or_404(Transaction, id=accountant_id)
    if request.method == 'POST':
        form = TransactionUpdateForm(request.POST, instance=accountant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('all_transactions')
    else:
        form = TransactionUpdateForm(instance=accountant)
    context = {
        'form':form,
        'accountant': accountant
    }
    return render(request, 'users/admin_dashboard/accountant/accountant_detail.html', context)

# API

class LoginView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        
        user = authenticate(phone_number=phone_number, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
    
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
    
def export_customer_accounts_pdf(request):
    # Get all customer accounts
    accounts = CustomerAccount.objects.all().select_related('customer')
    
    # Prepare context data for the template
    context = {
        'accounts': accounts,
        'total_count': accounts.count()
    }
    
    # Render template
    template = get_template('users/admin_dashboard/customer_accounts_pdf.html')
    html = template.render(context)
    
    # Create PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="customer_accounts.pdf"'
        return response
    
    return HttpResponse('Error generating PDF: %s' % pdf.err)



from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.serializers import serialize, deserialize
from django.db import transaction
import json
from django.contrib.auth import get_user_model
from django.utils import timezone
import os
from django.conf import settings
from django.core.files.base import ContentFile
import base64
from .models import Branch, Owner, Agent, Mobilization, Driver, Customer
from agent.models import BankDeposit as AgentBankDeposit
from agent.models import PaymentRequest as AgentPaymentRequest
from agent.models import CashAndECashRequest
from mobilization.models import BankDeposit, PaymentRequest
from decimal import Decimal

User = get_user_model()
# Users Import/Export
@csrf_exempt
@require_http_methods(["GET"])
def export_users(request):
    """Export User data as JSON download"""
    try:
        include_sensitive = request.GET.get('include_sensitive', 'false').lower() == 'true'
        users = User.objects.all()
        
        if include_sensitive:
            data = serialize('json', users)
        else:
            # Create safe export without sensitive data
            safe_data = []
            for user in users:
                safe_user = {
                    'model': 'auth.user',
                    'pk': user.pk,
                    'fields': {
                        'role': user.role,
                        'phone_number': user.phone_number,
                        'email': user.email,
                        'is_approved': user.is_approved,
                        'is_blocked': user.is_blocked,
                        'is_staff': user.is_staff,
                        'is_active': user.is_active,
                        'last_login': user.last_login.isoformat() if user.last_login else None,
                        'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                    }
                }
                safe_data.append(safe_user)
            data = json.dumps(safe_data)
        
        response = HttpResponse(data, content_type='application/json')
        filename = f'users_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def import_users(request):
    """Import User data from uploaded JSON file"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        data = uploaded_file.read().decode('utf-8')
        
        # Validate JSON
        try:
            json.loads(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON file'}, status=400)
        
        clear_existing = request.POST.get('clear_existing', 'false').lower() == 'true'
        skip_duplicates = request.POST.get('skip_duplicates', 'false').lower() == 'true'
        
        count = 0
        skipped = 0
        with transaction.atomic():
            # Clear existing data if specified
            if clear_existing:
                User.objects.all().delete()
            
            # Import data
            for obj in deserialize('json', data):
                user_data = obj.object
                
                # Check for duplicates
                if skip_duplicates and User.objects.filter(phone_number=user_data.phone_number).exists():
                    skipped += 1
                    continue
                
                # Handle password for new users
                if not hasattr(user_data, 'password') or not user_data.password:
                    user_data.set_password('default_password')
                
                obj.save()
                count += 1
        
        return JsonResponse({
            'message': f'Successfully imported {count} users, skipped {skipped} duplicates',
            'imported_count': count,
            'skipped_count': skipped
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
# Branch Import/Export

@csrf_exempt
@require_http_methods(["GET"])
def export_branches(request):
    """Export Branch data as JSON download"""
    try:
        branches = Branch.objects.all()
        data = serialize('json', branches)
        
        response = HttpResponse(data, content_type='application/json')
        filename = f'branches_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def import_branches(request):
    """Import Branch data from uploaded JSON file"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        data = uploaded_file.read().decode('utf-8')
        
        # Validate JSON
        try:
            json.loads(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON file'}, status=400)
        
        clear_existing = request.POST.get('clear_existing', 'false').lower() == 'true'
        skip_duplicates = request.POST.get('skip_duplicates', 'false').lower() == 'true'
        update_existing = request.POST.get('update_existing', 'false').lower() == 'true'
        
        count = 0
        updated = 0
        skipped = 0
        with transaction.atomic():
            # Clear existing data if specified
            if clear_existing:
                Branch.objects.all().delete()
            
            # Import data
            for obj in deserialize('json', data):
                branch_data = obj.object
                
                # Check for existing branch by name
                existing_branch = None
                if branch_data.name:
                    existing_branch = Branch.objects.filter(name=branch_data.name).first()
                
                if existing_branch:
                    if skip_duplicates:
                        skipped += 1
                        continue
                    elif update_existing:
                        # Update existing branch
                        existing_branch.location = branch_data.location
                        existing_branch.save()
                        updated += 1
                        continue
                
                obj.save()
                count += 1
        
        return JsonResponse({
            'message': f'Successfully imported {count} branches, updated {updated}, skipped {skipped}',
            'imported_count': count,
            'updated_count': updated,
            'skipped_count': skipped
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
# Owner Import/Export
@csrf_exempt
@require_http_methods(["GET"])
def export_owners(request):
    """Export Owner data as JSON download"""
    try:
        include_related = request.GET.get('include_related', 'false').lower() == 'true'
        owners = Owner.objects.all().select_related('owner', 'branch')
        
        if include_related:
            data = serialize('json', owners, use_natural_foreign_keys=True)
        else:
            # Create custom serialization
            custom_data = []
            for owner in owners:
                owner_data = {
                    'model': 'your_app.owner',
                    'pk': owner.pk,
                    'fields': {
                        'owner': owner.owner_id,
                        'branch': owner.branch_id if owner.branch else None,
                        'email': owner.email,
                        'full_name': owner.full_name,
                        'phone_number': owner.phone_number,
                        'company_name': owner.company_name,
                        'company_number': owner.company_number,
                        'digital_address': owner.digital_address,
                        'agent_code': owner.agent_code,
                    }
                }
                custom_data.append(owner_data)
            data = json.dumps(custom_data)
        
        response = HttpResponse(data, content_type='application/json')
        filename = f'owners_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def import_owners(request):
    """Import Owner data from uploaded JSON file"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        data = uploaded_file.read().decode('utf-8')
        
        # Validate JSON
        try:
            json.loads(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON file'}, status=400)
        
        clear_existing = request.POST.get('clear_existing', 'false').lower() == 'true'
        skip_duplicates = request.POST.get('skip_duplicates', 'false').lower() == 'true'
        update_existing = request.POST.get('update_existing', 'false').lower() == 'true'
        skip_missing_users = request.POST.get('skip_missing_users', 'false').lower() == 'true'
        
        count = 0
        updated = 0
        skipped = 0
        missing_users = 0
        with transaction.atomic():
            # Clear existing data if specified
            if clear_existing:
                Owner.objects.all().delete()
            
            # Import data
            for obj in deserialize('json', data):
                owner_data = obj.object
                
                # Check if user exists
                try:
                    user = User.objects.get(pk=owner_data.owner_id)
                except User.DoesNotExist:
                    if skip_missing_users:
                        missing_users += 1
                        continue
                    else:
                        return JsonResponse({
                            'error': f'User with ID {owner_data.owner_id} does not exist'
                        }, status=400)
                
                # Check for existing owner by user
                existing_owner = Owner.objects.filter(owner=user).first()
                
                if existing_owner:
                    if skip_duplicates:
                        skipped += 1
                        continue
                    elif update_existing:
                        # Update existing owner
                        existing_owner.branch = owner_data.branch
                        existing_owner.email = owner_data.email
                        existing_owner.full_name = owner_data.full_name
                        existing_owner.phone_number = owner_data.phone_number
                        existing_owner.company_name = owner_data.company_name
                        existing_owner.company_number = owner_data.company_number
                        existing_owner.digital_address = owner_data.digital_address
                        existing_owner.agent_code = owner_data.agent_code
                        existing_owner.save()
                        updated += 1
                        continue
                
                obj.save()
                count += 1
        
        return JsonResponse({
            'message': f'Successfully imported {count} owners, updated {updated}, skipped {skipped}, missing users: {missing_users}',
            'imported_count': count,
            'updated_count': updated,
            'skipped_count': skipped,
            'missing_users_count': missing_users
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

# Agents Import/Export
@csrf_exempt
@require_http_methods(["GET"])
def export_agents(request):
    """Export Agent data as JSON download"""
    try:
        include_related = request.GET.get('include_related', 'false').lower() == 'true'
        agents = Agent.objects.all().select_related('agent', 'owner', 'branch')
        
        if include_related:
            data = serialize('json', agents, use_natural_foreign_keys=True)
        else:
            # Create custom serialization
            custom_data = []
            for agent in agents:
                agent_data = {
                    'model': 'users.agent',
                    'pk': agent.pk,
                    'fields': {
                        'agent': agent.agent_id,
                        'owner': agent.owner_id,
                        'branch': agent.branch_id if agent.branch else None,
                        'email': agent.email,
                        'full_name': agent.full_name,
                        'phone_number': agent.phone_number,
                        'company_name': agent.company_name,
                        'company_number': agent.company_number,
                        'digital_address': agent.digital_address,
                        'agent_code': agent.agent_code,
                    }
                }
                custom_data.append(agent_data)
            data = json.dumps(custom_data)
        
        response = HttpResponse(data, content_type='application/json')
        filename = f'agents_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def import_agents(request):
    """Import Agent data from uploaded JSON file"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        data = uploaded_file.read().decode('utf-8')
        
        # Validate JSON
        try:
            json.loads(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON file'}, status=400)
        
        clear_existing = request.POST.get('clear_existing', 'false').lower() == 'true'
        skip_duplicates = request.POST.get('skip_duplicates', 'false').lower() == 'true'
        update_existing = request.POST.get('update_existing', 'false').lower() == 'true'
        skip_missing_users = request.POST.get('skip_missing_users', 'false').lower() == 'true'
        skip_missing_owners = request.POST.get('skip_missing_owners', 'false').lower() == 'true'
        
        count = 0
        updated = 0
        skipped = 0
        missing_users = 0
        missing_owners = 0
        with transaction.atomic():
            # Clear existing data if specified
            if clear_existing:
                Agent.objects.all().delete()
            
            # Import data
            for obj in deserialize('json', data):
                agent_data = obj.object
                
                # Check if user exists
                try:
                    user = User.objects.get(pk=agent_data.agent_id)
                except User.DoesNotExist:
                    if skip_missing_users:
                        missing_users += 1
                        continue
                    else:
                        return JsonResponse({
                            'error': f'User with ID {agent_data.agent_id} does not exist'
                        }, status=400)
                
                # Check if owner exists
                try:
                    owner = Owner.objects.get(pk=agent_data.owner_id)
                except Owner.DoesNotExist:
                    if skip_missing_owners:
                        missing_owners += 1
                        continue
                    else:
                        return JsonResponse({
                            'error': f'Owner with ID {agent_data.owner_id} does not exist'
                        }, status=400)
                
                # Check for existing agent by user
                existing_agent = Agent.objects.filter(agent=user).first()
                
                if existing_agent:
                    if skip_duplicates:
                        skipped += 1
                        continue
                    elif update_existing:
                        # Update existing agent
                        existing_agent.owner = owner
                        existing_agent.branch = agent_data.branch
                        existing_agent.email = agent_data.email
                        existing_agent.full_name = agent_data.full_name
                        existing_agent.phone_number = agent_data.phone_number
                        existing_agent.company_name = agent_data.company_name
                        existing_agent.company_number = agent_data.company_number
                        existing_agent.digital_address = agent_data.digital_address
                        existing_agent.agent_code = agent_data.agent_code
                        existing_agent.save()
                        updated += 1
                        continue
                
                obj.save()
                count += 1
        
        return JsonResponse({
            'message': f'Successfully imported {count} agents, updated {updated}, skipped {skipped}, missing users: {missing_users}, missing owners: {missing_owners}',
            'imported_count': count,
            'updated_count': updated,
            'skipped_count': skipped,
            'missing_users_count': missing_users,
            'missing_owners_count': missing_owners
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

# Mobilizalitions Import/Export
@csrf_exempt
@require_http_methods(["GET"])
def export_mobilizations(request):
    """Export Mobilization data as JSON download"""
    try:
        include_related = request.GET.get('include_related', 'false').lower() == 'true'
        mobilizations = Mobilization.objects.all().select_related('mobilization', 'owner', 'branch')
        
        if include_related:
            data = serialize('json', mobilizations, use_natural_foreign_keys=True)
        else:
            # Create custom serialization
            custom_data = []
            for mob in mobilizations:
                mob_data = {
                    'model': 'users.mobilization',
                    'pk': mob.pk,
                    'fields': {
                        'mobilization': mob.mobilization_id,
                        'owner': mob.owner_id if mob.owner else None,
                        'branch': mob.branch_id if mob.branch else None,
                        'email': mob.email,
                        'full_name': mob.full_name,
                        'phone_number': mob.phone_number,
                        'company_name': mob.company_name,
                        'company_number': mob.company_number,
                        'digital_address': mob.digital_address,
                        'mobilization_code': mob.mobilization_code,
                    }
                }
                custom_data.append(mob_data)
            data = json.dumps(custom_data)
        
        response = HttpResponse(data, content_type='application/json')
        filename = f'mobilizations_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def import_mobilizations(request):
    """Import Mobilization data from uploaded JSON file"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        data = uploaded_file.read().decode('utf-8')
        
        # Validate JSON
        try:
            json.loads(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON file'}, status=400)
        
        clear_existing = request.POST.get('clear_existing', 'false').lower() == 'true'
        skip_duplicates = request.POST.get('skip_duplicates', 'false').lower() == 'true'
        update_existing = request.POST.get('update_existing', 'false').lower() == 'true'
        skip_missing_users = request.POST.get('skip_missing_users', 'false').lower() == 'true'
        skip_missing_owners = request.POST.get('skip_missing_owners', 'false').lower() == 'true'
        
        count = 0
        updated = 0
        skipped = 0
        missing_users = 0
        missing_owners = 0
        with transaction.atomic():
            # Clear existing data if specified
            if clear_existing:
                Mobilization.objects.all().delete()
            
            # Import data
            for obj in deserialize('json', data):
                mob_data = obj.object
                
                # Check if user exists
                try:
                    user = User.objects.get(pk=mob_data.mobilization_id)
                except User.DoesNotExist:
                    if skip_missing_users:
                        missing_users += 1
                        continue
                    else:
                        return JsonResponse({
                            'error': f'User with ID {mob_data.mobilization_id} does not exist'
                        }, status=400)
                
                # Check if owner exists (if specified)
                owner = None
                if mob_data.owner_id:
                    try:
                        owner = Owner.objects.get(pk=mob_data.owner_id)
                    except Owner.DoesNotExist:
                        if skip_missing_owners:
                            missing_owners += 1
                            continue
                        else:
                            return JsonResponse({
                                'error': f'Owner with ID {mob_data.owner_id} does not exist'
                            }, status=400)
                
                # Check for existing mobilization by user
                existing_mob = Mobilization.objects.filter(mobilization=user).first()
                
                if existing_mob:
                    if skip_duplicates:
                        skipped += 1
                        continue
                    elif update_existing:
                        # Update existing mobilization
                        existing_mob.owner = owner
                        existing_mob.branch = mob_data.branch
                        existing_mob.email = mob_data.email
                        existing_mob.full_name = mob_data.full_name
                        existing_mob.phone_number = mob_data.phone_number
                        existing_mob.company_name = mob_data.company_name
                        existing_mob.company_number = mob_data.company_number
                        existing_mob.digital_address = mob_data.digital_address
                        existing_mob.mobilization_code = mob_data.mobilization_code
                        existing_mob.save()
                        updated += 1
                        continue
                
                obj.save()
                count += 1
        
        return JsonResponse({
            'message': f'Successfully imported {count} mobilizations, updated {updated}, skipped {skipped}, missing users: {missing_users}, missing owners: {missing_owners}',
            'imported_count': count,
            'updated_count': updated,
            'skipped_count': skipped,
            'missing_users_count': missing_users,
            'missing_owners_count': missing_owners
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

# Driver Import/Export
@csrf_exempt
@require_http_methods(["GET"])
def export_drivers(request):
    """Export Driver data as JSON download"""
    try:
        include_related = request.GET.get('include_related', 'false').lower() == 'true'
        drivers = Driver.objects.all().select_related('driver')
        
        if include_related:
            data = serialize('json', drivers, use_natural_foreign_keys=True)
        else:
            # Create custom serialization
            custom_data = []
            for driver in drivers:
                driver_data = {
                    'model': 'users.driver',
                    'pk': driver.pk,
                    'fields': {
                        'driver': driver.driver_id,
                        'email': driver.email,
                        'full_name': driver.full_name,
                        'phone_number': driver.phone_number,
                        'company_name': driver.company_name,
                        'company_number': driver.company_number,
                        'digital_address': driver.digital_address,
                        'driver_code': driver.driver_code,
                    }
                }
                custom_data.append(driver_data)
            data = json.dumps(custom_data)
        
        response = HttpResponse(data, content_type='application/json')
        filename = f'drivers_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def import_drivers(request):
    """Import Driver data from uploaded JSON file"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        data = uploaded_file.read().decode('utf-8')
        
        # Validate JSON
        try:
            json.loads(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON file'}, status=400)
        
        clear_existing = request.POST.get('clear_existing', 'false').lower() == 'true'
        skip_duplicates = request.POST.get('skip_duplicates', 'false').lower() == 'true'
        update_existing = request.POST.get('update_existing', 'false').lower() == 'true'
        skip_missing_users = request.POST.get('skip_missing_users', 'false').lower() == 'true'
        
        count = 0
        updated = 0
        skipped = 0
        missing_users = 0
        with transaction.atomic():
            # Clear existing data if specified
            if clear_existing:
                Driver.objects.all().delete()
            
            # Import data
            for obj in deserialize('json', data):
                driver_data = obj.object
                
                # Check if user exists
                try:
                    user = User.objects.get(pk=driver_data.driver_id)
                except User.DoesNotExist:
                    if skip_missing_users:
                        missing_users += 1
                        continue
                    else:
                        return JsonResponse({
                            'error': f'User with ID {driver_data.driver_id} does not exist'
                        }, status=400)
                
                # Check for existing driver by user
                existing_driver = Driver.objects.filter(driver=user).first()
                
                if existing_driver:
                    if skip_duplicates:
                        skipped += 1
                        continue
                    elif update_existing:
                        # Update existing driver
                        existing_driver.email = driver_data.email
                        existing_driver.full_name = driver_data.full_name
                        existing_driver.phone_number = driver_data.phone_number
                        existing_driver.company_name = driver_data.company_name
                        existing_driver.company_number = driver_data.company_number
                        existing_driver.digital_address = driver_data.digital_address
                        existing_driver.driver_code = driver_data.driver_code
                        existing_driver.save()
                        updated += 1
                        continue
                
                obj.save()
                count += 1
        
        return JsonResponse({
            'message': f'Successfully imported {count} drivers, updated {updated}, skipped {skipped}, missing users: {missing_users}',
            'imported_count': count,
            'updated_count': updated,
            'skipped_count': skipped,
            'missing_users_count': missing_users
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

# Custom Views for Import/Export Templates
@csrf_exempt
@require_http_methods(["GET"])
def export_customers(request):
    """Export Customer data as JSON download"""
    try:
        include_related = request.GET.get('include_related', 'false').lower() == 'true'
        include_images = request.GET.get('include_images', 'false').lower() == 'true'
        customers = Customer.objects.all().select_related('customer', 'agent', 'mobilization', 'branch')
        
        if include_related:
            data = serialize('json', customers, use_natural_foreign_keys=True)
        else:
            # Create custom serialization
            custom_data = []
            for customer in customers:
                customer_data = {
                    'model': 'users.customer',
                    'pk': customer.pk,
                    'fields': {
                        'customer': customer.customer_id,
                        'agent': customer.agent_id if customer.agent else None,
                        'mobilization': customer.mobilization_id if customer.mobilization else None,
                        'branch': customer.branch_id if customer.branch else None,
                        'phone_number': customer.phone_number,
                        'full_name': customer.full_name,
                        'customer_location': customer.customer_location,
                        'digital_address': customer.digital_address,
                        'id_type': customer.id_type,
                        'id_number': customer.id_number,
                        'date_of_birth': customer.date_of_birth.isoformat() if customer.date_of_birth else None,
                        'customer_picture': _handle_image_export(customer.customer_picture, include_images),
                        'customer_image': _handle_image_export(customer.customer_image, include_images),
                        'date_created': customer.date_created.isoformat() if customer.date_created else None,
                    }
                }
                custom_data.append(customer_data)
            data = json.dumps(custom_data)
        
        response = HttpResponse(data, content_type='application/json')
        filename = f'customers_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def import_customers(request):
    """Import Customer data from uploaded JSON file"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        data = uploaded_file.read().decode('utf-8')
        
        # Validate JSON
        try:
            json.loads(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON file'}, status=400)
        
        clear_existing = request.POST.get('clear_existing', 'false').lower() == 'true'
        skip_duplicates = request.POST.get('skip_duplicates', 'false').lower() == 'true'
        update_existing = request.POST.get('update_existing', 'false').lower() == 'true'
        skip_missing_users = request.POST.get('skip_missing_users', 'false').lower() == 'true'
        skip_missing_agents = request.POST.get('skip_missing_agents', 'false').lower() == 'true'
        skip_missing_mobilizations = request.POST.get('skip_missing_mobilizations', 'false').lower() == 'true'
        handle_images = request.POST.get('handle_images', 'false').lower() == 'true'
        
        count = 0
        updated = 0
        skipped = 0
        missing_users = 0
        missing_agents = 0
        missing_mobilizations = 0
        with transaction.atomic():
            # Clear existing data if specified
            if clear_existing:
                Customer.objects.all().delete()
            
            # Import data
            for obj in deserialize('json', data):
                customer_data = obj.object
                
                # Check if user exists
                try:
                    user = User.objects.get(pk=customer_data.customer_id)
                except User.DoesNotExist:
                    if skip_missing_users:
                        missing_users += 1
                        continue
                    else:
                        return JsonResponse({
                            'error': f'User with ID {customer_data.customer_id} does not exist'
                        }, status=400)
                
                # Check if agent exists (if specified)
                agent = None
                if customer_data.agent_id:
                    try:
                        agent = Agent.objects.get(pk=customer_data.agent_id)
                    except Agent.DoesNotExist:
                        if skip_missing_agents:
                            missing_agents += 1
                            continue
                        else:
                            return JsonResponse({
                                'error': f'Agent with ID {customer_data.agent_id} does not exist'
                            }, status=400)
                
                # Check if mobilization exists (if specified)
                mobilization = None
                if customer_data.mobilization_id:
                    try:
                        mobilization = Mobilization.objects.get(pk=customer_data.mobilization_id)
                    except Mobilization.DoesNotExist:
                        if skip_missing_mobilizations:
                            missing_mobilizations += 1
                            continue
                        else:
                            return JsonResponse({
                                'error': f'Mobilization with ID {customer_data.mobilization_id} does not exist'
                            }, status=400)
                
                # Check for existing customer by user
                existing_customer = Customer.objects.filter(customer=user).first()
                
                if existing_customer:
                    if skip_duplicates:
                        skipped += 1
                        continue
                    elif update_existing:
                        # Update existing customer
                        existing_customer.agent = agent
                        existing_customer.mobilization = mobilization
                        existing_customer.branch = customer_data.branch
                        existing_customer.phone_number = customer_data.phone_number
                        existing_customer.full_name = customer_data.full_name
                        existing_customer.customer_location = customer_data.customer_location
                        existing_customer.digital_address = customer_data.digital_address
                        existing_customer.id_type = customer_data.id_type
                        existing_customer.id_number = customer_data.id_number
                        existing_customer.date_of_birth = customer_data.date_of_birth
                        
                        # Handle images if specified
                        if handle_images:
                            existing_customer.customer_picture = _handle_image_import(customer_data.customer_picture, 'customer_pic')
                            existing_customer.customer_image = _handle_image_import(customer_data.customer_image, 'customer_image')
                        
                        existing_customer.save()
                        updated += 1
                        continue
                
                # Handle images for new customers if specified
                if handle_images:
                    customer_data.customer_picture = _handle_image_import(customer_data.customer_picture, 'customer_pic')
                    customer_data.customer_image = _handle_image_import(customer_data.customer_image, 'customer_image')
                
                obj.save()
                count += 1
        
        return JsonResponse({
            'message': f'Successfully imported {count} customers, updated {updated}, skipped {skipped}, missing users: {missing_users}, missing agents: {missing_agents}, missing mobilizations: {missing_mobilizations}',
            'imported_count': count,
            'updated_count': updated,
            'skipped_count': skipped,
            'missing_users_count': missing_users,
            'missing_agents_count': missing_agents,
            'missing_mobilizations_count': missing_mobilizations
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def _handle_image_export(image_field, include_images):
    """Handle image field export"""
    if not image_field:
        return None
    
    if include_images and image_field:
        try:
            with open(image_field.path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except (FileNotFoundError, ValueError):
            return None
    else:
        return image_field.name if image_field else None

def _handle_image_import(image_data, upload_to):
    """Handle image import"""
    if not image_data:
        return None
    
    if isinstance(image_data, str) and len(image_data) > 1000:  # Likely base64
        try:
            format, imgstr = image_data.split(';base64,') if ';base64,' in image_data else (None, image_data)
            ext = 'png' if not format else format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{upload_to}_{timezone.now().timestamp()}.{ext}')
            return data
        except (ValueError, TypeError):
            return None
    return image_data


# Mobilization Models Import/Export Views
# BankDeposit Import/Export Views

@csrf_exempt
@require_http_methods(["GET"])
def export_bank_deposits(request):
    """Export BankDeposit data as JSON download"""
    try:
        include_related = request.GET.get('include_related', 'false').lower() == 'true'
        include_images = request.GET.get('include_images', 'false').lower() == 'true'
        deposits = BankDeposit.objects.all().select_related('mobilization')
        
        if include_related:
            data = serialize('json', deposits, use_natural_foreign_keys=True)
        else:
            # Create custom serialization
            custom_data = []
            for deposit in deposits:
                deposit_data = {
                    'model': 'mobilization.bankdeposit',
                    'pk': deposit.pk,
                    'fields': {
                        'mobilization': deposit.mobilization_id if deposit.mobilization else None,
                        'phone_number': deposit.phone_number,
                        'bank': deposit.bank,
                        'account_number': deposit.account_number,
                        'account_name': deposit.account_name,
                        'amount': str(deposit.amount),
                        'receipt': _handle_image_export(deposit.receipt, include_images),
                        'owner_transaction_id': deposit.owner_transaction_id,
                        'screenshot': _handle_image_export(deposit.screenshot, include_images),
                        'screenshot2': _handle_image_export(deposit.screenshot2, include_images),
                        'screenshot3': _handle_image_export(deposit.screenshot3, include_images),
                        'screenshot4': _handle_image_export(deposit.screenshot4, include_images),
                        'screenshot5': _handle_image_export(deposit.screenshot5, include_images),
                        'screenshot6': _handle_image_export(deposit.screenshot6, include_images),
                        'screenshot7': _handle_image_export(deposit.screenshot7, include_images),
                        'screenshot8': _handle_image_export(deposit.screenshot8, include_images),
                        'screenshot9': _handle_image_export(deposit.screenshot9, include_images),
                        'screenshot10': _handle_image_export(deposit.screenshot10, include_images),
                        'status': deposit.status,
                        'date_deposited': deposit.date_deposited.isoformat() if deposit.date_deposited else None,
                        'time_deposited': deposit.time_deposited.isoformat() if deposit.time_deposited else None,
                    }
                }
                custom_data.append(deposit_data)
            data = json.dumps(custom_data)
        
        response = HttpResponse(data, content_type='application/json')
        filename = f'bank_deposits_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def import_bank_deposits(request):
    """Import BankDeposit data from uploaded JSON file"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        data = uploaded_file.read().decode('utf-8')
        
        # Validate JSON
        try:
            json.loads(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON file'}, status=400)
        
        clear_existing = request.POST.get('clear_existing', 'false').lower() == 'true'
        skip_missing_mobilizations = request.POST.get('skip_missing_mobilizations', 'false').lower() == 'true'
        handle_images = request.POST.get('handle_images', 'false').lower() == 'true'
        skip_duplicates = request.POST.get('skip_duplicates', 'false').lower() == 'true'
        
        count = 0
        skipped = 0
        missing_mobilizations = 0
        with transaction.atomic():
            # Clear existing data if specified
            if clear_existing:
                BankDeposit.objects.all().delete()
            
            # Import data
            for obj in deserialize('json', data):
                deposit_data = obj.object
                
                # Check if mobilization exists (if specified)
                mobilization = None
                if deposit_data.mobilization_id:
                    try:
                        mobilization = Mobilization.objects.get(pk=deposit_data.mobilization_id)
                    except Mobilization.DoesNotExist:
                        if skip_missing_mobilizations:
                            missing_mobilizations += 1
                            continue
                        else:
                            return JsonResponse({
                                'error': f'Mobilization with ID {deposit_data.mobilization_id} does not exist'
                            }, status=400)
                
                # Check for duplicates if skip_duplicates is True
                if skip_duplicates:
                    if deposit_data.owner_transaction_id:
                        existing_deposit = BankDeposit.objects.filter(
                            owner_transaction_id=deposit_data.owner_transaction_id
                        ).first()
                        if existing_deposit:
                            skipped += 1
                            continue
                    
                    existing_deposit = BankDeposit.objects.filter(
                        bank=deposit_data.bank,
                        account_number=deposit_data.account_number,
                        amount=deposit_data.amount,
                        date_deposited=deposit_data.date_deposited
                    ).first()
                    if existing_deposit:
                        skipped += 1
                        continue
                
                # Handle amount conversion
                if isinstance(deposit_data.amount, str):
                    try:
                        deposit_data.amount = Decimal(deposit_data.amount)
                    except (ValueError, TypeError):
                        deposit_data.amount = Decimal('0.00')
                
                # Handle images if specified
                if handle_images:
                    deposit_data.receipt = _handle_image_import(deposit_data.receipt, 'receipt_img')
                    deposit_data.screenshot = _handle_image_import(deposit_data.screenshot, 'screenshot_img')
                    deposit_data.screenshot2 = _handle_image_import(deposit_data.screenshot2, 'screenshot_img2')
                    deposit_data.screenshot3 = _handle_image_import(deposit_data.screenshot3, 'screenshot_img3')
                    deposit_data.screenshot4 = _handle_image_import(deposit_data.screenshot4, 'screenshot_img4')
                    deposit_data.screenshot5 = _handle_image_import(deposit_data.screenshot5, 'screenshot_img5')
                    deposit_data.screenshot6 = _handle_image_import(deposit_data.screenshot6, 'screenshot_img6')
                    deposit_data.screenshot7 = _handle_image_import(deposit_data.screenshot7, 'screenshot_img7')
                    deposit_data.screenshot8 = _handle_image_import(deposit_data.screenshot8, 'screenshot_img8')
                    deposit_data.screenshot9 = _handle_image_import(deposit_data.screenshot9, 'screenshot_img9')
                    deposit_data.screenshot10 = _handle_image_import(deposit_data.screenshot10, 'screenshot_img10')
                
                obj.save()
                count += 1
        
        return JsonResponse({
            'message': f'Successfully imported {count} bank deposits, skipped {skipped}, missing mobilizations: {missing_mobilizations}',
            'imported_count': count,
            'skipped_count': skipped,
            'missing_mobilizations_count': missing_mobilizations
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def _handle_image_export(image_field, include_images):
    """Handle image field export"""
    if not image_field:
        return None
    
    if include_images and image_field:
        try:
            with open(image_field.path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except (FileNotFoundError, ValueError):
            return None
    else:
        return image_field.name if image_field else None

def _handle_image_import(image_data, upload_to):
    """Handle image import"""
    if not image_data:
        return None
    
    if isinstance(image_data, str) and len(image_data) > 100:  # Likely base64
        try:
            if ';base64,' in image_data:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
            else:
                imgstr = image_data
                ext = 'png'
            
            data = ContentFile(base64.b64decode(imgstr), name=f'{upload_to}_{timezone.now().timestamp()}.{ext}')
            return data
        except (ValueError, TypeError):
            return None
    return image_data

# PaymentRequest Import/Export Views
@csrf_exempt
@require_http_methods(["GET"])
def export_payment_requests(request):
    """Export PaymentRequest data as JSON download"""
    try:
        include_related = request.GET.get('include_related', 'false').lower() == 'true'
        payment_requests = PaymentRequest.objects.all().select_related('mobilization')
        
        if include_related:
            data = serialize('json', payment_requests, use_natural_foreign_keys=True)
        else:
            # Create custom serialization
            custom_data = []
            for payment_request in payment_requests:
                payment_request_data = {
                    'model': 'mobilization.paymentrequest',
                    'pk': payment_request.pk,
                    'fields': {
                        'mobilization': payment_request.mobilization_id if payment_request.mobilization else None,
                        'mode_of_payment': payment_request.mode_of_payment,
                        'bank': payment_request.bank,
                        'network': payment_request.network,
                        'branch': payment_request.branch,
                        'name': payment_request.name,
                        'amount': str(payment_request.amount),
                        'mobilization_transaction_id': payment_request.mobilization_transaction_id,
                        'owner_transaction_id': payment_request.owner_transaction_id,
                        'status': payment_request.status,
                        'created_at': payment_request.created_at.isoformat() if payment_request.created_at else None,
                        'updated_at': payment_request.updated_at.isoformat() if payment_request.updated_at else None,
                    }
                }
                custom_data.append(payment_request_data)
            data = json.dumps(custom_data)
        
        response = HttpResponse(data, content_type='application/json')
        filename = f'payment_requests_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def import_payment_requests(request):
    """Import PaymentRequest data from uploaded JSON file"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        data = uploaded_file.read().decode('utf-8')
        
        # Validate JSON
        try:
            json.loads(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON file'}, status=400)
        
        clear_existing = request.POST.get('clear_existing', 'false').lower() == 'true'
        skip_missing_mobilizations = request.POST.get('skip_missing_mobilizations', 'false').lower() == 'true'
        skip_duplicates = request.POST.get('skip_duplicates', 'false').lower() == 'true'
        update_existing = request.POST.get('update_existing', 'false').lower() == 'true'
        
        count = 0
        updated = 0
        skipped = 0
        missing_mobilizations = 0
        with transaction.atomic():
            # Clear existing data if specified
            if clear_existing:
                PaymentRequest.objects.all().delete()
            
            # Import data
            for obj in deserialize('json', data):
                payment_request_data = obj.object
                
                # Check if mobilization exists
                mobilization = None
                if payment_request_data.mobilization_id:
                    try:
                        mobilization = Mobilization.objects.get(pk=payment_request_data.mobilization_id)
                    except Mobilization.DoesNotExist:
                        if skip_missing_mobilizations:
                            missing_mobilizations += 1
                            continue
                        else:
                            return JsonResponse({
                                'error': f'Mobilization with ID {payment_request_data.mobilization_id} does not exist'
                            }, status=400)
                
                # Handle amount conversion
                if isinstance(payment_request_data.amount, str):
                    try:
                        payment_request_data.amount = Decimal(payment_request_data.amount)
                    except (ValueError, TypeError):
                        payment_request_data.amount = Decimal('0.00')
                
                # Check for duplicates
                if skip_duplicates:
                    if payment_request_data.mobilization_transaction_id:
                        existing_request = PaymentRequest.objects.filter(
                            mobilization_transaction_id=payment_request_data.mobilization_transaction_id
                        ).first()
                        if existing_request:
                            if update_existing:
                                # Update existing payment request
                                existing_request.mobilization = mobilization
                                existing_request.mode_of_payment = payment_request_data.mode_of_payment
                                existing_request.bank = payment_request_data.bank
                                existing_request.network = payment_request_data.network
                                existing_request.branch = payment_request_data.branch
                                existing_request.name = payment_request_data.name
                                existing_request.amount = payment_request_data.amount
                                existing_request.owner_transaction_id = payment_request_data.owner_transaction_id
                                existing_request.status = payment_request_data.status
                                existing_request.save()
                                updated += 1
                                continue
                            else:
                                skipped += 1
                                continue
                    
                    if payment_request_data.owner_transaction_id:
                        existing_request = PaymentRequest.objects.filter(
                            owner_transaction_id=payment_request_data.owner_transaction_id
                        ).first()
                        if existing_request:
                            if update_existing:
                                # Update existing payment request
                                existing_request.mobilization = mobilization
                                existing_request.mode_of_payment = payment_request_data.mode_of_payment
                                existing_request.bank = payment_request_data.bank
                                existing_request.network = payment_request_data.network
                                existing_request.branch = payment_request_data.branch
                                existing_request.name = payment_request_data.name
                                existing_request.amount = payment_request_data.amount
                                existing_request.mobilization_transaction_id = payment_request_data.mobilization_transaction_id
                                existing_request.status = payment_request_data.status
                                existing_request.save()
                                updated += 1
                                continue
                            else:
                                skipped += 1
                                continue
                
                obj.save()
                count += 1
        
        return JsonResponse({
            'message': f'Successfully imported {count} payment requests, updated {updated}, skipped {skipped}, missing mobilizations: {missing_mobilizations}',
            'imported_count': count,
            'updated_count': updated,
            'skipped_count': skipped,
            'missing_mobilizations_count': missing_mobilizations
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

# Agent BankDeposit Import/Export Views
@csrf_exempt
@require_http_methods(["GET"])
def export_agent_bank_deposits(request):
    """Export BankDeposit data as JSON download"""
    try:
        include_related = request.GET.get('include_related', 'false').lower() == 'true'
        include_images = request.GET.get('include_images', 'false').lower() == 'true'
        deposits = AgentBankDeposit.objects.all().select_related('agent')
        
        if include_related:
            data = serialize('json', deposits, use_natural_foreign_keys=True)
        else:
            # Create custom serialization
            custom_data = []
            for deposit in deposits:
                deposit_data = {
                    'model': 'agent.bankdeposit',
                    'pk': deposit.pk,
                    'fields': {
                        'agent': deposit.agent_id if deposit.agent else None,
                        'phone_number': deposit.phone_number,
                        'bank': deposit.bank,
                        'account_number': deposit.account_number,
                        'account_name': deposit.account_name,
                        'amount': str(deposit.amount),
                        'receipt': _handle_image_export(deposit.receipt, include_images),
                        'date_deposited': deposit.date_deposited.isoformat() if deposit.date_deposited else None,
                        'time_deposited': deposit.time_deposited.isoformat() if deposit.time_deposited else None,
                    }
                }
                custom_data.append(deposit_data)
            data = json.dumps(custom_data)
        
        response = HttpResponse(data, content_type='application/json')
        filename = f'bank_deposits_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def import_agent_bank_deposits(request):
    """Import BankDeposit data from uploaded JSON file"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        data = uploaded_file.read().decode('utf-8')
        
        # Validate JSON
        try:
            json.loads(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON file'}, status=400)
        
        clear_existing = request.POST.get('clear_existing', 'false').lower() == 'true'
        skip_missing_agents = request.POST.get('skip_missing_agents', 'false').lower() == 'true'
        handle_images = request.POST.get('handle_images', 'false').lower() == 'true'
        skip_duplicates = request.POST.get('skip_duplicates', 'false').lower() == 'true'
        
        count = 0
        skipped = 0
        missing_agents = 0
        with transaction.atomic():
            # Clear existing data if specified
            if clear_existing:
                AgentBankDeposit.objects.all().delete()
            
            # Import data
            for obj in deserialize('json', data):
                deposit_data = obj.object
                
                # Check if agent exists
                agent = None
                if deposit_data.agent_id:
                    try:
                        agent = Agent.objects.get(pk=deposit_data.agent_id)
                    except Agent.DoesNotExist:
                        if skip_missing_agents:
                            missing_agents += 1
                            continue
                        else:
                            return JsonResponse({
                                'error': f'Agent with ID {deposit_data.agent_id} does not exist'
                            }, status=400)
                
                # Check for duplicates if skip_duplicates is True
                if skip_duplicates:
                    existing_deposit = AgentBankDeposit.objects.filter(
                        bank=deposit_data.bank,
                        account_number=deposit_data.account_number,
                        amount=deposit_data.amount,
                        date_deposited=deposit_data.date_deposited
                    ).first()
                    if existing_deposit:
                        skipped += 1
                        continue
                
                # Handle amount conversion
                if isinstance(deposit_data.amount, str):
                    try:
                        deposit_data.amount = Decimal(deposit_data.amount)
                    except (ValueError, TypeError):
                        deposit_data.amount = Decimal('0.00')
                
                # Handle images if specified
                if handle_images:
                    deposit_data.receipt = _handle_image_import(deposit_data.receipt, 'branch_receipt_img')
                
                obj.save()
                count += 1
        
        return JsonResponse({
            'message': f'Successfully imported {count} bank deposits, skipped {skipped}, missing agents: {missing_agents}',
            'imported_count': count,
            'skipped_count': skipped,
            'missing_agents_count': missing_agents
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def _handle_image_export(image_field, include_images):
    """Handle image field export"""
    if not image_field:
        return None
    
    if include_images and image_field:
        try:
            with open(image_field.path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except (FileNotFoundError, ValueError):
            return None
    else:
        return image_field.name if image_field else None

def _handle_image_import(image_data, upload_to):
    """Handle image import"""
    if not image_data:
        return None
    
    if isinstance(image_data, str) and len(image_data) > 100:  # Likely base64
        try:
            if ';base64,' in image_data:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]
            else:
                imgstr = image_data
                ext = 'png'
            
            data = ContentFile(base64.b64decode(imgstr), name=f'{upload_to}_{timezone.now().timestamp()}.{ext}')
            return data
        except (ValueError, TypeError):
            return None
    return image_data


# Agent CashAndECashRequest Import/Export Views
@csrf_exempt
@require_http_methods(["GET"])
def export_cash_ecash_requests(request):
    """Export CashAndECashRequest data as JSON download"""
    try:
        include_related = request.GET.get('include_related', 'false').lower() == 'true'
        requests = CashAndECashRequest.objects.all().select_related('agent')
        
        if include_related:
            data = serialize('json', requests, use_natural_foreign_keys=True)
        else:
            # Create custom serialization
            custom_data = []
            for request in requests:
                request_data = {
                    'model': 'your_app.cashandecashrequest',
                    'pk': request.pk,
                    'fields': {
                        'agent': request.agent_id if request.agent else None,
                        'float_type': request.float_type,
                        'bank': request.bank,
                        'transaction_id': request.transaction_id,
                        'network': request.network,
                        'cash': request.cash,
                        'name': request.name,
                        'phone_number': request.phone_number,
                        'amount': str(request.amount),
                        'arrears': str(request.arrears),
                        'status': request.status,
                        'created_at': request.created_at.isoformat() if request.created_at else None,
                        'time_created': request.time_created.isoformat() if request.time_created else None,
                        'updated_at': request.updated_at.isoformat() if request.updated_at else None,
                    }
                }
                custom_data.append(request_data)
            data = json.dumps(custom_data)
        
        response = HttpResponse(data, content_type='application/json')
        filename = f'cash_ecash_requests_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def import_cash_ecash_requests(request):
    """Import CashAndECashRequest data from uploaded JSON file"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        data = uploaded_file.read().decode('utf-8')
        
        # Validate JSON
        try:
            json.loads(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON file'}, status=400)
        
        clear_existing = request.POST.get('clear_existing', 'false').lower() == 'true'
        skip_missing_agents = request.POST.get('skip_missing_agents', 'false').lower() == 'true'
        skip_duplicates = request.POST.get('skip_duplicates', 'false').lower() == 'true'
        update_existing = request.POST.get('update_existing', 'false').lower() == 'true'
        
        count = 0
        updated = 0
        skipped = 0
        missing_agents = 0
        with transaction.atomic():
            # Clear existing data if specified
            if clear_existing:
                CashAndECashRequest.objects.all().delete()
            
            # Import data
            for obj in deserialize('json', data):
                request_data = obj.object
                
                # Check if agent exists
                agent = None
                if request_data.agent_id:
                    try:
                        agent = Agent.objects.get(pk=request_data.agent_id)
                    except Agent.DoesNotExist:
                        if skip_missing_agents:
                            missing_agents += 1
                            continue
                        else:
                            return JsonResponse({
                                'error': f'Agent with ID {request_data.agent_id} does not exist'
                            }, status=400)
                
                # Handle amount conversion
                if isinstance(request_data.amount, str):
                    try:
                        request_data.amount = Decimal(request_data.amount)
                    except (ValueError, TypeError):
                        request_data.amount = Decimal('0.00')
                
                # Handle arrears conversion
                if isinstance(request_data.arrears, str):
                    try:
                        request_data.arrears = Decimal(request_data.arrears)
                    except (ValueError, TypeError):
                        request_data.arrears = Decimal('0.00')
                
                # Check for duplicates
                if skip_duplicates:
                    if request_data.transaction_id:
                        existing_request = CashAndECashRequest.objects.filter(
                            transaction_id=request_data.transaction_id
                        ).first()
                        if existing_request:
                            if update_existing:
                                # Update existing request
                                existing_request.agent = agent
                                existing_request.float_type = request_data.float_type
                                existing_request.bank = request_data.bank
                                existing_request.network = request_data.network
                                existing_request.cash = request_data.cash
                                existing_request.name = request_data.name
                                existing_request.phone_number = request_data.phone_number
                                existing_request.amount = request_data.amount
                                existing_request.arrears = request_data.arrears
                                existing_request.status = request_data.status
                                existing_request.save()
                                updated += 1
                                continue
                            else:
                                skipped += 1
                                continue
                    
                    existing_request = CashAndECashRequest.objects.filter(
                        agent=agent,
                        amount=request_data.amount,
                        created_at=request_data.created_at
                    ).first()
                    if existing_request:
                        if update_existing:
                            # Update existing request
                            existing_request.float_type = request_data.float_type
                            existing_request.bank = request_data.bank
                            existing_request.transaction_id = request_data.transaction_id
                            existing_request.network = request_data.network
                            existing_request.cash = request_data.cash
                            existing_request.name = request_data.name
                            existing_request.phone_number = request_data.phone_number
                            existing_request.arrears = request_data.arrears
                            existing_request.status = request_data.status
                            existing_request.save()
                            updated += 1
                            continue
                        else:
                            skipped += 1
                            continue
                
                obj.save()
                count += 1
        
        return JsonResponse({
            'message': f'Successfully imported {count} cash/ecash requests, updated {updated}, skipped {skipped}, missing agents: {missing_agents}',
            'imported_count': count,
            'updated_count': updated,
            'skipped_count': skipped,
            'missing_agents_count': missing_agents
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
# Agent PaymentRequest Import/Export Views
@csrf_exempt
@require_http_methods(["GET"])
def export_agent_payment_requests(request):
    """Export PaymentRequest data as JSON download"""
    try:
        include_related = request.GET.get('include_related', 'false').lower() == 'true'
        payment_requests = AgentPaymentRequest.objects.all().select_related('agent')
        
        if include_related:
            data = serialize('json', payment_requests, use_natural_foreign_keys=True)
        else:
            # Create custom serialization
            custom_data = []
            for payment_request in payment_requests:
                payment_request_data = {
                    'model': 'agent.paymentrequest',
                    'pk': payment_request.pk,
                    'fields': {
                        'agent': payment_request.agent_id if payment_request.agent else None,
                        'mode_of_payment': payment_request.mode_of_payment,
                        'bank': payment_request.bank,
                        'network': payment_request.network,
                        'branch': payment_request.branch,
                        'name': payment_request.name,
                        'branch_transaction_id': payment_request.branch_transaction_id,
                        'amount': str(payment_request.amount),
                        'status': payment_request.status,
                        'created_at': payment_request.created_at.isoformat() if payment_request.created_at else None,
                        'time_created': payment_request.time_created.isoformat() if payment_request.time_created else None,
                        'updated_at': payment_request.updated_at.isoformat() if payment_request.updated_at else None,
                    }
                }
                custom_data.append(payment_request_data)
            data = json.dumps(custom_data)
        
        response = HttpResponse(data, content_type='application/json')
        filename = f'payment_requests_backup_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def import_agent_payment_requests(request):
    """Import PaymentRequest data from uploaded JSON file"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        uploaded_file = request.FILES['file']
        data = uploaded_file.read().decode('utf-8')
        
        # Validate JSON
        try:
            json.loads(data)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON file'}, status=400)
        
        clear_existing = request.POST.get('clear_existing', 'false').lower() == 'true'
        skip_missing_agents = request.POST.get('skip_missing_agents', 'false').lower() == 'true'
        skip_duplicates = request.POST.get('skip_duplicates', 'false').lower() == 'true'
        update_existing = request.POST.get('update_existing', 'false').lower() == 'true'
        skip_duplicate_transaction_id = request.POST.get('skip_duplicate_transaction_id', 'false').lower() == 'true'
        
        count = 0
        updated = 0
        skipped = 0
        missing_agents = 0
        duplicate_transaction_ids = 0
        with transaction.atomic():
            # Clear existing data if specified
            if clear_existing:
                AgentPaymentRequest.objects.all().delete()
            
            # Import data
            for obj in deserialize('json', data):
                payment_request_data = obj.object
                
                # Check if agent exists
                agent = None
                if payment_request_data.agent_id:
                    try:
                        agent = Agent.objects.get(pk=payment_request_data.agent_id)
                    except Agent.DoesNotExist:
                        if skip_missing_agents:
                            missing_agents += 1
                            continue
                        else:
                            return JsonResponse({
                                'error': f'Agent with ID {payment_request_data.agent_id} does not exist'
                            }, status=400)
                
                # Handle amount conversion
                if isinstance(payment_request_data.amount, str):
                    try:
                        payment_request_data.amount = Decimal(payment_request_data.amount)
                    except (ValueError, TypeError):
                        payment_request_data.amount = Decimal('0.00')
                
                # Check for duplicate branch_transaction_id if specified
                if skip_duplicate_transaction_id and payment_request_data.branch_transaction_id:
                    existing_with_same_id = AgentPaymentRequest.objects.filter(
                        branch_transaction_id=payment_request_data.branch_transaction_id
                    ).exists()
                    if existing_with_same_id:
                        duplicate_transaction_ids += 1
                        continue
                
                # Check for duplicates
                if skip_duplicates:
                    existing_request = AgentPaymentRequest.objects.filter(
                        agent=agent,
                        amount=payment_request_data.amount,
                        created_at=payment_request_data.created_at
                    ).first()
                    if existing_request:
                        if update_existing:
                            # Update existing payment request
                            existing_request.mode_of_payment = payment_request_data.mode_of_payment
                            existing_request.bank = payment_request_data.bank
                            existing_request.network = payment_request_data.network
                            existing_request.branch = payment_request_data.branch
                            existing_request.name = payment_request_data.name
                            existing_request.branch_transaction_id = payment_request_data.branch_transaction_id
                            existing_request.status = payment_request_data.status
                            existing_request.save()
                            updated += 1
                            continue
                        else:
                            skipped += 1
                            continue
                
                obj.save()
                count += 1
        
        return JsonResponse({
            'message': f'Successfully imported {count} payment requests, updated {updated}, skipped {skipped}, missing agents: {missing_agents}, duplicate transaction IDs: {duplicate_transaction_ids}',
            'imported_count': count,
            'updated_count': updated,
            'skipped_count': skipped,
            'missing_agents_count': missing_agents,
            'duplicate_transaction_ids_count': duplicate_transaction_ids
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




    
def all_backups(request):
    return render(request, 'users/imports/all_backups/backup.html')

def user_import_export(request):
    return render(request, 'users/imports/all_backups/users.html')

def branch_import_export(request):
    return render(request, 'users/imports/all_backups/branches.html')

def owner_import_export(request):
    return render(request, 'users/imports/all_backups/owners.html')

def agent_import_export(request):
    return render(request, 'users/imports/all_backups/agents.html')

def mobilization_import_export(request):
    return render(request, 'users/imports/all_backups/mobilization.html')

def driver_import_export(request):
    return render(request, 'users/imports/all_backups/driver.html')

def customer_import_export(request):
    return render(request, 'users/imports/all_backups/customers.html')

def mobilization_bank_deposit_import_export(request):
    return render(request, 'users/imports/all_backups/mobilization/bank_deposit.html')

def mobilization_payment_request_import_export(request):
    return render(request, 'users/imports/all_backups/mobilization/payment.html')

def agent_bank_deposit_import_export(request):
    return render(request, 'users/imports/all_backups/agent/bank_deposit.html')

def agent_cash_ecash_import_export(request):
    return render(request, 'users/imports/all_backups/agent/cash_ecash.html')

def agent_payment_request_import_export(request):
    return render(request, 'users/imports/all_backups/agent/payment.html')