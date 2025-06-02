# forms.py
from django import forms
from .models import Transaction, TransactionCategory, Vehicle

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['network_or_bank', 'transaction_id', 'vehicle', 'branch', 'transaction_type', 'amount', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            # 'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['category'].queryset = TransactionCategory.objects.all()
    
class TransactionUpdateForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['network_or_bank', 'transaction_id', 'vehicle', 'branch', 'transaction_type', 'amount', 'description', 'date']
        widgets = {
                'date': forms.DateInput(attrs={'type': 'date'}),
                # 'description': forms.Textarea(attrs={'rows': 3}),
            }
        
class MonthYearFilterForm(forms.Form):
    MONTH_CHOICES = [
        ('', 'All Months'),
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]
    
    YEAR_CHOICES = [
        ('', 'All Years'),
        ('2023', '2023'),
        ('2024', '2024'),
        ('2025', '2025'),
        # Add more years as needed
    ]
    
    month = forms.ChoiceField(choices=MONTH_CHOICES, required=False)
    year = forms.ChoiceField(choices=YEAR_CHOICES, required=False)