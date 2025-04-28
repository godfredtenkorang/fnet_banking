from django import forms
from .models import MileageRecord, FuelRecord, Expense


class MileageRecordForm(forms.ModelForm):
    class Meta:
        model = MileageRecord
        fields = ['vehicle', 'date', 'start_mileage', 'end_mileage']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
class FuelRecordForm(forms.ModelForm):
    class Meta:
        model = FuelRecord
        fields = ['vehicle', 'date', 'liters', 'amount', 'station_name', 'receipt_number']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'type', 'amount', 'description', 'receipt']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5, 'cols': 60}),
        }