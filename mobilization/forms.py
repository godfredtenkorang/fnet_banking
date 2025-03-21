from django import forms

class CustomerFilterForm(forms.Form):
    phone_number = forms.CharField(required=False, label='Phone Number')