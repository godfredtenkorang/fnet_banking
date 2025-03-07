from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput

from .models import User, Branch, Owner, Agent, Customer

class UserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=[('OWNER', 'Owner'),('AGENT', 'Agent')],  # Removed "Admin"
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class Meta:
        model = User
        fields = ['username', 'phone_number', 'password1', 'password2', 'role']
        
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
        
class OwnerRegistrationForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.filter(role='OWNER'), required=True)
    class Meta:
        model = Owner
        fields = ['user', 'branch', 'email', 'full_name', 'phone_number', 'company_name', 'company_number', 'digital_address', 'agent_code']

class AgentRegistrationForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.filter(role='AGENT'), required=True)
    class Meta:
        model = Agent
        fields = ['user', 'owner', 'branch', 'email', 'full_name', 'phone_number', 'company_name', 'company_number', 'digital_address', 'agent_code']

class CustomerRegistrationForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.filter(role='CUSTOMER'), required=True)
    
    class Meta:
        model = Customer
        fields = ['user', 'agent', 'branch', 'phone_number', 'full_name', 'customer_location', 'digital_address', 'id_type', 'id_number', 'date_of_birth', 'customer_picture']
        
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
        'required': 'required'
    }), label='')
    password = forms.CharField(widget=PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
        'required': 'required'
    }), label='')