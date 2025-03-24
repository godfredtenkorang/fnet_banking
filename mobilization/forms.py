from django import forms
from .models import BankDeposit, Report

class CustomerFilterForm(forms.Form):
    phone_number = forms.CharField(required=False, label='Phone Number')
    
class UpdateBankDepositForm(forms.ModelForm):
    class Meta:
        model = BankDeposit
        fields = ['screenshot',]
        
        
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report',]