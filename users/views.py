from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import auth
from django.contrib.auth.backends import ModelBackend

from agent.serializers import TransactionSerializer
from .forms import UserRegisterForm, OwnerRegistrationForm, DriverRegistrationForm, CustomPasswordChangeForm, AgentRegistrationForm, CustomerRegistrationForm, LoginForm, MobilizationRegistrationForm
from .models import User, Owner, Agent, Customer, Branch, Mobilization, OTPToken, Driver
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
from django.db.models import Sum


from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView



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
                elif user.is_blocked:
                    messages.error(request, "Your account has been blocked. Please contact the admin.")
                else:
                    messages.error(request, "Your account is not yet approved by the admin.")
            else:
                user.generate_otp()
                send_otp(user.phone_number, user.otp)
                request.session['phone_number'] = phone_number  # Store phone number in session
                send_otp_via_email(user.email, user.otp)
                return redirect('verify_otp')
        else:
            messages.error(request, 'Invalid phone number or password.')
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
                    elif user.role == "DRIVER":
                        return redirect("driver_dashboard")
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
    
    context = {
        'admins': admins,
        'owners': owners,
        'agents': agents,
        'mobilizations': mobilizations,
        'drivers': drivers,
        'customers': customers,
        'title': 'Users'

    }
    return render(request, 'users/admin_dashboard/users.html', context)

def birthdays(request):
    return render(request, 'users/admin_dashboard/birthdays.html')


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
    
    
