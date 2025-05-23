import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput

from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm

from .models import User, Branch, Owner, Agent, Customer, Mobilization, Driver, Accountant

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)  # Optional email field
    role = forms.ChoiceField(
        choices=[('OWNER', 'Owner'),('BRANCH', 'Branch'), ('MOBILIZATION', 'Mobilization'), ('DRIVER', 'Driver'), ('ACCOUNTANT', 'Accountant')],  # Removed "Admin"
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
        
class DriverRegistrationForm(forms.ModelForm):
    driver = forms.ModelChoiceField(queryset=User.objects.filter(role='DRIVER'), required=True)
    class Meta:
        model = Driver
        fields = ['driver', 'email', 'full_name', 'phone_number', 'company_name', 'company_number', 'digital_address', 'driver_code']

class AccountantRegistrationForm(forms.ModelForm):
    accountant = forms.ModelChoiceField(queryset=User.objects.filter(role='ACCOUNTANT'), required=True)
    class Meta:
        model = Accountant
        fields = ['accountant', 'email', 'full_name', 'phone_number', 'company_name', 'company_number', 'digital_address', 'accountant_code']

class AgentRegistrationForm(forms.ModelForm):
    agent = forms.ModelChoiceField(queryset=User.objects.filter(role='BRANCH'), required=True)
    class Meta:
        model = Agent
        fields = ['agent', 'owner', 'branch', 'email', 'full_name', 'phone_number', 'company_name', 'company_number', 'digital_address', 'agent_code']

class CustomerRegistrationForm(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset=User.objects.filter(role='CUSTOMER'), required=True)
    
    class Meta:
        model = Customer
        fields = ['customer', 'agent', 'branch', 'phone_number', 'full_name', 'customer_location', 'digital_address', 'id_type', 'id_number', 'date_of_birth', 'customer_picture', 'customer_image']
        
class CustomerUpdateForm(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset=User.objects.filter(role='CUSTOMER'), required=True)
    
    class Meta:
        model = Customer
        fields = ['customer', 'branch', 'phone_number', 'full_name', 'customer_location', 'digital_address', 'id_type', 'id_number', 'date_of_birth', 'customer_picture', 'customer_image']
        
class CustomerFilterForm(forms.Form):
    phone_number = forms.CharField(required=False, label='Phone Number')
    
class AccountFilterForm(forms.Form):
    phone_number = forms.CharField(required=False, label='Phone Number')
    
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
    
    
class CustomPasswordChangeForm(PasswordChangeForm):
    """
    A form that lets a user change their password by entering their old password
    along with OTP verification (handled in the view).
    """
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
    )

    def __init__(self, *args, **kwargs):
        # Remove the old password field since we're using OTP verification
        super().__init__(*args, **kwargs)
        self.fields.pop('old_password', None)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        password_validation.validate_password(password2, self.user)
        return password2
    
class SecurePasswordChangeForm(CustomPasswordChangeForm):
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        
        # Check if password is different from last 3 passwords
        if self.user.check_password(password):
            raise forms.ValidationError(
                _("Your new password must be different from your current password."),
                code='password_same_as_current',
            )
            
        # Add any additional password policy checks here
        return password