from django.db import models
from django.utils import timezone
from users.models import User


class Branch(models.Model):
    BRANCH_CHOICES = [
        ('HO', 'Head Office'),
        ('KEJ', 'Kejetia Branch'),
        ('DVL', 'DVLA Branch'),
        ('ADM', 'Adum Melcom'),
        ('ADX', 'Adum Annex Melcom'),
        ('TAN', 'Tanoso Melcom'),
        ('SUA', 'Suame Melcom'),
        ('SAN', 'Santasi Melcom'),
        ('AHO', 'Ahodwo Melcom'),
        ('TAC', 'Taco Melcom'),
        ('KUM', 'Kumasi Mall'),
        ('MAN', 'Manhyia Melcom'),
        ('TOF', 'Tofo Melcom'),
        ('MOB', 'Mobilization Team'),
    ]
    
    
    name = models.CharField(max_length=100, choices=BRANCH_CHOICES)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Vehicle(models.Model):
    license_plate = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.license_plate})"


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
    ACCOUNT = (
        ('MTN', 'MTN'),
        ('Ecobank', 'Ecobank'),
    )
    network_or_bank = models.CharField(max_length=100, choices=ACCOUNT, null=True, blank=True)
    transaction_id = models.CharField(max_length=50, unique=True, null=True, blank=True, default='')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')
    # category = models.ForeignKey(TransactionCategory, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=250, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, default='', related_name='transactions')
    date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            # Generate transaction ID if not provided
            prefix = 'INC' if self.transaction_type == 'income' else 'EXP'
            last_id = Transaction.objects.filter(transaction_id__startswith=prefix).count()
            self.transaction_id = f"{prefix}-{last_id + 1:04d}"
        super().save(*args, **kwargs)
    
    
    def __str__(self):
        return f"{self.transaction_id} - {self.get_transaction_type_display()} - {self.amount}"