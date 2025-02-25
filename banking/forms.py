from django import forms
from .models import Drawer


class DrawerDepositForm(forms.ModelForm):
    class Meta:
        model = Drawer
        fields = ['opening_balance']