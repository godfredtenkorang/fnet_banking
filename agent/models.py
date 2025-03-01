from django.db import models
from django.conf import settings
from users.models import Agent
from django.utils import timezone

# Create your models here.

User = settings.AUTH_USER_MODEL

MOBILE_MONEY_DEPOSIT_TYPE = (
    ("Loading", "Loading"),
    ("Deposit", "Deposit"),
)

NETWORKS = (
    ("Select Network", "Select Network"),
    ("Mtn", "Mtn"),
    ("Telecel", "Telecel"),
    ("AirtelTigo", "AirtelTigo"),
)

REQUEST_STATUS = (
    ("Pending", "Pending"),
    ("Approved", "Approved"),
    ("Rejected", "Rejected")
)

class CustomerCashIn(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_cash_ins")
    network = models.CharField(max_length=20, choices=NETWORKS, blank=True, default="Select Network")
    customer_phone = models.CharField(max_length=10, blank=True)
    # customer_name = models.CharField(max_length=30, blank=True)
    deposit_type = models.CharField(max_length=20, blank=True, choices=MOBILE_MONEY_DEPOSIT_TYPE)
    depositor_name = models.CharField(max_length=30, blank=True, default="")
    depositor_number = models.CharField(max_length=30, blank=True, default="")
    # reference = models.CharField(max_length=100, blank=True, default="")
    amount = models.DecimalField(max_digits=19, decimal_places=2, blank=True)
    # charges = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    # agent_commission = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    date_deposited = models.DateField(auto_now_add=True)
    time_deposited = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"CashIn of ${self.amount} on {self.network} by {self.depositor_name}"
    

class CustomerCashOut(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_cash_outs")
    network = models.CharField(max_length=20, choices=NETWORKS, blank=True, default="Select Network")
    customer_phone = models.CharField(max_length=10, blank=True)
    # customer_name = models.CharField(max_length=30, blank=True)
    # reference = models.CharField(max_length=100, blank=True, default="")
    amount = models.DecimalField(max_digits=19, decimal_places=2, blank=True)
    # charges = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    # agent_commission = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    date_withdrawn = models.DateField(auto_now_add=True)
    time_withdrawn = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"CashOut of ${self.amount} on {self.network} by {self.customer_phone}"
    

class BankDeposit(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='bank_deposits')
    phone_number = models.CharField(max_length=10)
    bank = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=100, choices=REQUEST_STATUS, default='Pending')
    date_deposited = models.DateField(default=timezone.now)
    time_deposited = models.TimeField(default=timezone.now)
    
    def __str__(self):
        return f"Bank Deposit of GH¢{self.amount} to {self.bank} by {self.phone_number} ({self.status})"
    
    


class BankWithdrawal(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='bank_withdrawals')
    customer_phone = models.CharField(max_length=15)
    bank = models.CharField(max_length=20)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_withdrawn = models.DateField(default=timezone.now)
    time_withdrawn = models.TimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='Pending')
    
    def __str__(self):
        return f"Bank Withdrawal of GH¢{self.amount} from {self.bank} by {self.customer_phone} ({self.status})"
    
    
class CashAndECashRequest(models.Model):
    FLOAT_TYPE_CHOICES = [
        ('Bank', 'Bank'),
        ('Telco', 'Telco'),
        ('Cash', 'Cash'),
    ]

    BANK_CHOICES = [
        ('Select Bank', 'Select Bank'),
        ('Ecobank', 'Ecobank'),
        ('Fidelity', 'Fidelity'),
        ('Calbank', 'Calbank'),
        ('GTBank', 'GTBank'),
        ('Access Bank', 'Access Bank'),
    ]

    NETWORK_CHOICES = [
        ('Select Network', 'Select Network'),
        ('MTN', 'MTN'),
        ('Telecel', 'Telecel'),
        ('AirtelTigo', 'AirtelTigo'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='cash_and_ecash_requests')
    float_type = models.CharField(max_length=10, choices=FLOAT_TYPE_CHOICES)
    bank = models.CharField(max_length=20, choices=BANK_CHOICES, default='Select Bank', null=True, blank=True)
    network = models.CharField(max_length=20, choices=NETWORK_CHOICES, default='Select Network', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Track remaining balance
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.float_type} Request of GH¢{self.amount} by {self.agent.user.username}"