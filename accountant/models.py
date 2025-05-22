from django.db import models
from django.utils import timezone
from users.models import User, Vehicle


class TransactionCategory(models.Model):
    name = models.CharField(max_length=100)
    is_income = models.BooleanField(default=False)  # True for income, False for expense
    
    def __str__(self):
        return self.name

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    
    transaction_id = models.CharField(max_length=50, unique=True, null=True, blank=True, default='')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')
    # category = models.ForeignKey(TransactionCategory, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=250, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.get_transaction_type_display()} - {self.amount}"