from django import forms
from .models import BankDeposit, Report
from users.models import User, Customer


class CustomerFilterForm(forms.Form):
    phone_number = forms.CharField(required=False, label='Phone Number')
    
class UpdateBankDepositForm(forms.ModelForm):
    class Meta:
        model = BankDeposit
        fields = ['screenshot', 'screenshot2', 'screenshot3', 'screenshot4', 'screenshot5', 'screenshot6', 'screenshot7', 'screenshot8', 'screenshot9', 'screenshot10']
        
        
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report',]
        
class CustomerImageUpdateForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ['customer_picture' ,'customer_image']
        