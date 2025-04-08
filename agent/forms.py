from django import forms
from users.models import Customer
from .models import BankDeposit

class CustomerFilterForm(forms.Form):
    phone_number = forms.CharField(required=False, label='Phone Number')
    
    
class CustomerImageUpdateForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ['customer_picture' ,'customer_image']
        
