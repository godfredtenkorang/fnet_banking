from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import auth
from django.contrib.auth.backends import ModelBackend
from .forms import UserRegisterForm, OwnerRegistrationForm, AgentRegistrationForm, CustomerRegistrationForm, LoginForm, MobilizationRegistrationForm
from .models import User, Owner, Agent, Customer, Branch, Mobilization
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from .utils import send_otp, send_otp_via_email, generate_otp, send_otp_sms
from django.utils import timezone




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
        user = authenticate(request, username=phone_number, password=password)
        
        
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
    customers = User.objects.filter(role="CUSTOMER")
    
    context = {
        'admins': admins,
        'owners': owners,
        'agents': agents,
        'mobilizations': mobilizations,
        'customers': customers,
        'title': 'Users'

    }
    return render(request, 'users/admin_dashboard/users.html', context)

def birthdays(request):
    return render(request, 'users/admin_dashboard/birthdays.html')