from django import forms
from .models import BankDeposit

class CustomerFilterForm(forms.Form):
    phone_number = forms.CharField(required=False, label='Phone Number')
    
class UpdateBankDepositForm(forms.ModelForm):
    class Meta:
        model = BankDeposit
        fields = ['screenshot',]