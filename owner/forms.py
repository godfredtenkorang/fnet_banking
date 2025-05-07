from django import forms
from mobilization.models import BankDeposit, PaymentRequest
from users.models import Mobilization
from .models import OwnerBalance


class BankDepositForm(forms.ModelForm):
    class Meta:
        model = BankDeposit
        fields = ['mobilization', 'phone_number', 'bank', 'account_number', 'account_name', 'amount', 'status']
        
        
class PaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentRequest
        fields = ['mobilization', 'mode_of_payment', 'bank', 'network', 'branch', 'name', 'amount', 'owner_transaction_id', 'status']
        
class OwnerBalanceForm(forms.ModelForm):
    
    class Meta:
        model = OwnerBalance
        fields = [
            'cash_balance',
            'mtn_balance', 
            'telecel_balance',
            'airteltigo_balance',
            'ecobank_balance',
            'gtbank_balance',
            'fidelity_balance',
            'calbank_balance',
            'access_bank_balance'
        ]
        widgets = {
            'cash_balance': forms.NumberInput(attrs={'class': 'form-control'}),
            'mtn_balance': forms.NumberInput(attrs={'class': 'form-control'}),
            # Add widgets for other fields similarly
        }