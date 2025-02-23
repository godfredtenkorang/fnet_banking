from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import PasswordInput, TextInput

from .models import User, Branch, Owner, Agent, Customer

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'phone_number', 'password1', 'password2', 'role']
        
class OwnerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ['branch']

class AgentRegistrationForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['owner', 'branch']

class CustomerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['agent', 'branch']
        
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