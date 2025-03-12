from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import auth
from .forms import UserRegisterForm, OwnerRegistrationForm, AgentRegistrationForm, CustomerRegistrationForm, LoginForm, MobilizationRegistrationForm
from .models import User, Owner, Agent, Customer, Branch, Mobilization
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required



def all_requests(request):
    return render(request, 'users/admin_dashboard/request.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
        
    context = {
        'form': form
    }
    return render(request, 'users/register.html', context)


def login_user(request):
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        user = authenticate(request, username=phone_number, password=password)
        
        
        if user is not None:
            if user.is_approved and not user.is_blocked:
                login(request, user)
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
            messages.error(request, "Invalid username or password.")
                

        
    context = {
      
        'title': 'Login'
    }
    
    return render(request, 'users/login.html', context)


def logout(request):
    auth.logout(request)
    
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
    users = User.objects.all()
    
    context = {
        'users': users,
        'title': 'Users'

    }
    return render(request, 'users/admin_dashboard/users.html', context)

def birthdays(request):
    return render(request, 'users/admin_dashboard/birthdays.html')