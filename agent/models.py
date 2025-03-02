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
    

class PaymentRequest(models.Model):
    MODE_OF_PAYMENT = [
        ('Telco', 'Telco'),
        ('Bank', 'Bank'),
        ('Branch', 'Branch'),
    ]
    
    BANK_CHOICES = [
        ("Select bank", "Select bank"),
        ("Access Bank", "Access Bank"),
        ("Cal Bank", "Cal Bank"),
        ("Fidelity Bank", "Fidelity Bank"),
        ("Ecobank", "Ecobank"),
        ("GT Bank", "GT Bank"),
        ("Adansi rural bank", "Adansi rural bank"),
        ("Kwumawuman Bank", "Kwumawuman Bank"),
        ("Pan Africa", "Pan Africa"),
        ("SGSSB", "SGSSB"),
        ("Atwima Rural Bank", "Atwima Rural Bank"),
        ("Omnibsic Bank", "Omnibsic Bank"),
        ("Omini bank", "Omini bank"),
        ("Stanbic Bank", "Stanbic Bank"),
        ("First Bank of Nigeria", "First Bank of Nigeria"),
        ("Adehyeman Savings and loans", "Adehyeman Savings and loans",),
        ("ARB Apex Bank Limited", "ARB Apex Bank Limited",),
        ("Absa Bank", "Absa Bank"),
        ("Agriculture Development bank", "Agriculture Development bank"),
        ("Bank of Africa", "Bank of Africa"),
        ("Bank of Ghana", "Bank of Ghana"),
        ("Consolidated Bank Ghana", "Consolidated Bank Ghana"),
        ("First Atlantic Bank", "First Atlantic Bank"),
        ("First National Bank", "First National Bank"),
        ("G-Money", "G-Money"),
        ("GCB BanK LTD", "GCB BanK LTD"),
        ("Ghana Pay", "Ghana Pay"),
        ("GHL Bank Ltd", "GHL Bank Ltd"),
        ("National Investment Bank", "National Investment Bank"),
        ("Opportunity International Savings And Loans", "Opportunity International Savings And Loans"),
        ("Prudential Bank", "Prudential Bank"),
        ("Republic Bank Ltd", "Republic Bank Ltd"),
        ("Sahel Sahara Bank", "Sahel Sahara Bank"),
        ("Sinapi Aba Savings and Loans", "Sinapi Aba Savings and Loans"),
        ("Societe Generale Ghana Ltd", "Societe Generale Ghana Ltd"),
        ("Standard Chartered", "Standard Chartered"),
        ("universal Merchant Bank", "universal Merchant Bank"),
        ("Zenith Bank", "Zenith Bank"),
        ("Mtn", "Mtn"),
        ("AirtelTigo", "AirtelTigo"),
        ("Telecel", "Telecel"),
    ]

    NETWORK_CHOICES = [
        ('Select Network', 'Select Network'),
        ('MTN', 'MTN'),
        ('Telecel', 'Telecel'),
        ('AirtelTigo', 'AirtelTigo'),
    ]
    
    BRANCHES = (
        ("DVLA", "DVLA"),
        ("HEAD OFFICE", "HEAD OFFICE"),
        ("KEJETIA", "KEJETIA"),
        ("MELCOM SANTASI", "MELCOM SANTASI"),
        ("MELCOM TANOSO", "MELCOM TANOSO"),
        ("MELCOM MANHYIA", "MELCOM MANHYIA"),
        ("MELCOM TAFO", "MELCOM TAFO"),
        ("AHODWO MELCOM", "AHODWO MELCOM"),
        ("ADUM MELCOM ANNEX", "ADUM MELCOM ANNEX"),
        ("MELCOM SUAME", "MELCOM SUAME"),
        ("KUMASI MALL MELCOM", "KUMASI MALL MELCOM"),
        ("MOBILIZATION", "MOBILIZATION"),
    )
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='payments_requests')
    mode_of_payment = models.CharField(max_length=10, choices=MODE_OF_PAYMENT, null=True, blank=True)
    bank = models.CharField(max_length=50, choices=BANK_CHOICES, null= True, blank=True)
    network = models.CharField(max_length=30, choices=NETWORK_CHOICES, null= True, blank=True)
    branch = models.CharField(max_length=30, choices=BRANCHES, null= True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment of ${self.amount} via {self.mode_of_payment} by {self.agent.user.username} ({self.status})"
    
    
class CustomerComplain(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Complain from {self.agent.user.username} - {self.title}"
    

class HoldCustomerAccount(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    amount = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=10)
    agent_number = models.CharField(max_length=10)
    transaction_id = models.CharField(max_length=100)
    reasons = models.TextField()
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Hold Account of {self.customer_phone} ({self.transaction_id})"
    
    
class CustomerFraud(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    customer_phone = models.CharField(max_length=10)
    reasons = models.TextField()
    date = models.DateField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"Fraud alert from {self.customer_phone} - {self.reasons}"