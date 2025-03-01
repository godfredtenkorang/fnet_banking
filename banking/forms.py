from django import forms
from .models import Drawer, EFloatAccount


class DrawerDepositForm(forms.ModelForm):
    class Meta:
        model = Drawer
        fields = ['opening_balance']
        
class EFloatAccountForm(forms.ModelForm):
    class Meta:
        model = EFloatAccount
        fields = [
            'mtn_balance', 'telecel_balance', 'airtel_tigo_balance', 'ecobank_balance', 
            'fidelity_balance', 'calbank_balance', 'gtbank_balance', 'access_bank_balance',
            'cash_at_hand'
        ]
    
        
class AddCapitalForm(forms.Form):
    additional_capital = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, label="Additional Capital Amount")