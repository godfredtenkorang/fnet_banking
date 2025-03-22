from django import forms
from mobilization.models import BankDeposit, PaymentRequest
from users.models import Mobilization


class BankDepositForm(forms.ModelForm):
    class Meta:
        model = BankDeposit
        fields = ['mobilization', 'phone_number', 'bank', 'account_number', 'account_name', 'amount', 'status']
        
        
class PaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentRequest
        fields = ['mobilization', 'mode_of_payment', 'bank', 'network', 'branch', 'name', 'amount', 'mobilization_transaction_id', 'owner_transaction_id', 'status']
        