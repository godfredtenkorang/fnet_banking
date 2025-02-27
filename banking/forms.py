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
            'mtn_balance', 'telecel_balance', 'ecobank_balance', 
            'fidelity_balance', 'calbank_balance', 'gtbank_balance', 
            'cash_at_hand'
        ]