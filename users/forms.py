import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput

from .models import User, Branch, Owner, Agent, Customer, Mobilization

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)  # Optional email field
    role = forms.ChoiceField(
        choices=[('OWNER', 'Owner'),('BRANCH', 'Branch'), ('MOBILIZATION', 'Mobilization')],  # Removed "Admin"
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = User
        fields = ['phone_number', 'email', 'password1', 'password2', 'role']
        
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        
        for fieldname in ['password1', 'password2']:
            self.fields[fieldname].help_text = None
            
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            raise forms.ValidationError('Invalid phone number format.')
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError('This phone number is already registered.')
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', password1):
            raise forms.ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password1):
            raise forms.ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', password1):
            raise forms.ValidationError('Password must contain at least one digit.')
        return password1
        
class OwnerRegistrationForm(forms.ModelForm):
    owner = forms.ModelChoiceField(queryset=User.objects.filter(role='OWNER'), required=True)
    class Meta:
        model = Owner
        fields = ['owner', 'branch', 'email', 'full_name', 'phone_number', 'company_name', 'company_number', 'digital_address', 'agent_code']

class AgentRegistrationForm(forms.ModelForm):
    agent = forms.ModelChoiceField(queryset=User.objects.filter(role='BRANCH'), required=True)
    class Meta:
        model = Agent
        fields = ['agent', 'owner', 'branch', 'email', 'full_name', 'phone_number', 'company_name', 'company_number', 'digital_address', 'agent_code']

class CustomerRegistrationForm(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset=User.objects.filter(role='CUSTOMER'), required=True)
    
    class Meta:
        model = Customer
        fields = ['customer', 'agent', 'branch', 'phone_number', 'full_name', 'customer_location', 'digital_address', 'id_type', 'id_number', 'date_of_birth', 'customer_picture']
    
class MobilizationRegistrationForm(forms.ModelForm):
    mobilization = forms.ModelChoiceField(queryset=User.objects.filter(role='MOBILIZATION'), required=True)
    class Meta:
        model = Mobilization
        fields = ['mobilization', 'owner', 'branch', 'email', 'full_name', 'phone_number', 'company_name', 'company_number', 'digital_address', 'mobilization_code']
        
class LoginForm(AuthenticationForm):
    phone_number = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            raise forms.ValidationError('Invalid phone number format.')
        return phone_number