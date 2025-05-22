# forms.py
from django import forms
from .models import Transaction, TransactionCategory

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_id', 'vehicle', 'transaction_type', 'amount', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            # 'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['category'].queryset = TransactionCategory.objects.all()