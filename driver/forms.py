from django import forms
from .models import MileageRecord, FuelRecord, Expense, OilChange, Notification


class MileageRecordForm(forms.ModelForm):
    class Meta:
        model = MileageRecord
        fields = ['vehicle', 'date', 'start_mileage', 'end_mileage']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
class UpdateMileageRecordForm(forms.ModelForm):
    class Meta:
        model = MileageRecord
        fields = ['end_mileage']
        
        
class FuelRecordForm(forms.ModelForm):
    class Meta:
        model = FuelRecord
        fields = ['vehicle', 'date', 'liters', 'amount', 'station_name', 'receipt']
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
        
class OilChangeForm(forms.ModelForm):
    class Meta:
        model = OilChange
        fields = ['vehicle', 'date', 'mileage', 'cost']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['message', 'notification_type']
        