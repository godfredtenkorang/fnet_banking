from django import forms
from .models import MileageRecord, FuelRecord, Expense, OilChange, Notification
from users.models import Vehicle


class MileageRecordForm(forms.ModelForm):
    input_unit = forms.ChoiceField(
        choices=Vehicle.UNIT_CHOICES,
        initial='km',
        widget=forms.HiddenInput()
    )
    class Meta:
        model = MileageRecord
        fields = ['vehicle', 'date', 'start_mileage', 'end_mileage', 'input_unit']
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
    input_unit = forms.ChoiceField(
        choices=Vehicle.UNIT_CHOICES,
        initial='km',
        widget=forms.HiddenInput()
    )
    class Meta:
        model = OilChange
        fields = ['vehicle', 'date', 'mileage', 'cost', 'input_unit']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        vehicle = kwargs.pop('vehicle', None)
        super().__init__(*args, **kwargs)
        if vehicle:
            self.fields['input_unit'].initial = vehicle.distance_unit
        
class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['message', 'notification_type']
        