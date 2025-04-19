from django.db import models
from django.conf import settings
from users.models import Agent
from django.utils import timezone
from django.db.models import Sum
from decimal  import Decimal

# Create your models here.

User = settings.AUTH_USER_MODEL

from django.db import models
from django.utils import timezone

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('CASH_IN', 'Cash In'),
        ('CASH_OUT', 'Cash Out'),
        ('PAY_TO', 'Pay To'),
        ('AGENT_PAYOUT', 'Agent Payout'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    transaction_type = models.CharField(max_length=12, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    recipient_phone = models.CharField(max_length=20, blank=True, null=True)
    reference = models.CharField(max_length=50, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_succussful = models.BooleanField(default=False)
        
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.transaction_type} - {self.phone_number} - {self.amount}"


MOBILE_MONEY_DEPOSIT_TYPE = (
    ("Loading", "Loading"),
    ("Direct", "Direct"),
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
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="customer_cash_ins")
    network = models.CharField(max_length=20, choices=NETWORKS, blank=True, default="Select Network")
    customer_phone = models.CharField(max_length=10, blank=True)
    # customer_name = models.CharField(max_length=30, blank=True)
    deposit_type = models.CharField(max_length=20, blank=True, choices=MOBILE_MONEY_DEPOSIT_TYPE)
    depositor_name = models.CharField(max_length=30, blank=True, default="")
    depositor_number = models.CharField(max_length=30, blank=True, default="")
    # reference = models.CharField(max_length=100, blank=True, default="")
    amount = models.DecimalField(max_digits=19, decimal_places=2, blank=True)
    cash_received = models.DecimalField(max_digits=19, decimal_places=2, default=0.00, blank=True)
    # charges = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    # agent_commission = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    date_deposited = models.DateField(auto_now_add=True)
    time_deposited = models.TimeField(auto_now_add=True)
    is_fraudster = models.BooleanField(default=False)  # Track if the customer is a fraudster
    
    def check_fraud(self):
        if CustomerFraud.objects.filter(customer_phone=self.customer_phone).exists():
            self.is_fraudster = True
        else:
            self.is_fraudster = False
            
    def save(self, *args, **kwargs):
        # Check for fraud before saving
        self.check_fraud()
        
        # Save the CustomerCashIn instance
        super().save(*args, **kwargs)
    
    @classmethod
    def total_cash_for_customer(cls, agent):
        total = cls.objects.filter(agent=agent).aggregate(Sum('amount'))
        return total['amount__sum'] or 0
    
    def save(self, *args, **kwargs):
        commission_amount = self.cash_received - self.amount
        
        # Save the CustomerCashIn instance
        super().save(*args, **kwargs)
        
        CashInCommission.objects.update_or_create(
            customer_cash_in=self, defaults={'amount': commission_amount} 
        )

    def __str__(self):
        return f"CashIn of ${self.amount} on {self.network}"
    

class CashInCommission(models.Model):
    customer_cash_in = models.OneToOneField(CustomerCashIn, on_delete=models.CASCADE, related_name='cashincommission')
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Commission amount
    date = models.DateField(auto_now_add=True)  # Date of the commission
    
    def __str__(self):
        return f"Commission: {self.amount}"
    

class ArchivedCustomerCashIn(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    network = models.CharField(max_length=20, choices=NETWORKS, blank=True, default="Select Network")
    customer_phone = models.CharField(max_length=10, blank=True)
    # customer_name = models.CharField(max_length=30, blank=True)
    deposit_type = models.CharField(max_length=20, blank=True, choices=MOBILE_MONEY_DEPOSIT_TYPE)
    depositor_name = models.CharField(max_length=30, blank=True, default="")
    depositor_number = models.CharField(max_length=30, blank=True, default="")
    # reference = models.CharField(max_length=100, blank=True, default="")
    amount = models.DecimalField(max_digits=19, decimal_places=2, blank=True)
    cash_received = models.DecimalField(max_digits=19, decimal_places=2, default=0.00, blank=True)
    # charges = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    # agent_commission = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    date_deposited = models.DateField(auto_now_add=True)
    time_deposited = models.TimeField(auto_now_add=True)
    

    def __str__(self):
        return f"CashIn of ${self.amount} on {self.network}"
    

class ArchivedCashInCommission(models.Model):
    customer_cash_in = models.OneToOneField(CustomerCashIn, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Commission amount
    date = models.DateField(auto_now_add=True)  # Date of the commission
    
    def __str__(self):
        return f"Commission: {self.amount}"
    


class CustomerCashOut(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="customer_cash_outs")
    network = models.CharField(max_length=20, choices=NETWORKS, blank=True, default="Select Network")
    customer_phone = models.CharField(max_length=10, blank=True)
    # customer_name = models.CharField(max_length=30, blank=True)
    # reference = models.CharField(max_length=100, blank=True, default="")
    amount = models.DecimalField(max_digits=19, decimal_places=2, blank=True)
    cash_paid = models.DecimalField(max_digits=19, decimal_places=2, default=0.00, blank=True)
    # charges = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    # agent_commission = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    date_withdrawn = models.DateField(auto_now_add=True)
    time_withdrawn = models.TimeField(auto_now_add=True)
    
    @classmethod
    def total_cashout_for_customer(cls, agent):
        total = cls.objects.filter(agent=agent).aggregate(Sum('amount'))
        return total['amount__sum'] or 0
    
    def save(self, *args, **kwargs):
        commission_amount = self.cash_paid - self.amount
        
        # Save the CustomerCashIn instance
        super().save(*args, **kwargs)
        
        CashOutCommission.objects.update_or_create(
            customer_cash_out=self, defaults={'amount': commission_amount} 
        )

    def __str__(self):
        return f"CashOut of ${self.amount} on {self.network} by {self.customer_phone}"
    

class CashOutCommission(models.Model):
    customer_cash_out = models.OneToOneField(CustomerCashOut, on_delete=models.CASCADE, related_name='cashoutcommission')
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Commission amount
    date = models.DateField(auto_now_add=True)  # Date of the commission
    
    def __str__(self):
        return f"Commission: {self.amount} "


class BankDeposit(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='bank_deposits')
    phone_number = models.CharField(max_length=10)
    bank = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    receipt = models.ImageField(upload_to='branch_receipt_img/', default='', null=True, blank=True)
    # status = models.CharField(max_length=100, choices=REQUEST_STATUS, default='Pending')
    date_deposited = models.DateField(default=timezone.now)
    time_deposited = models.TimeField(default=timezone.now)
    
    @classmethod
    def total_bank_deposit_for_customer(cls, agent):
        total = cls.objects.filter(agent=agent).aggregate(Sum('amount'))
        return total['amount__sum'] or 0
    
    def __str__(self):
        return f"Bank Deposit of GH¢{self.amount} to {self.bank} by {self.phone_number}"
    
    


class BankWithdrawal(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='bank_withdrawals')
    customer_phone = models.CharField(max_length=15)
    bank = models.CharField(max_length=20)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    ghana_card = models.ImageField(upload_to='ghana_card_img/', default='', null=True, blank=True)
    date_withdrawn = models.DateField(default=timezone.now)
    time_withdrawn = models.TimeField(default=timezone.now)
    # status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='Pending')
    
    @classmethod
    def total_bank_withdrawal_for_customer(cls, agent):
        total = cls.objects.filter(agent=agent).aggregate(Sum('amount'))
        return total['amount__sum'] or 0
    
    def __str__(self):
        return f"Bank Withdrawal of GH¢{self.amount} from {self.bank} by {self.customer_phone}"
    
    
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
    
    CASH_CHOICES = [
        ('Cash', 'Cash'),
        
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
    cash = models.CharField(max_length=10, choices=CASH_CHOICES, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    arrears = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Track remaining balance
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    @classmethod
    def total_ecash_for_customer(cls, agent, status):
        total = cls.objects.filter(agent=agent, status=status).aggregate(Sum('amount'))
        return total['amount__sum'] or 0

    def __str__(self):
        return f"{self.float_type} Request of GH¢{self.amount} by {self.agent.phone_number}"
    

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
        ("ADUM MELCOM", "ADUM MELCOM"),
        ("ADUM MELCOM ANNEX", "ADUM MELCOM ANNEX"),
        ("MELCOM SUAME", "MELCOM SUAME"),
        ("KUMASI MALL MELCOM", "KUMASI MALL MELCOM"),
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
    name = models.CharField(max_length=100, null=True, blank=True)
    branch_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    @classmethod
    def total_payment_for_customer(cls, agent, status):
        total = cls.objects.filter(agent=agent, status=status).aggregate(Sum('amount'))
        return total['amount__sum'] or 0
    
    def __str__(self):
        return f"Payment of ${self.amount} via {self.mode_of_payment} by {self.agent.phone_number} ({self.status})"
    
    
class CustomerComplain(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Complain from {self.agent.phone_number} - {self.title}"
    

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
    



class CustomerPayTo(models.Model):
    PAY_TO_DEPOSIT_TYPE = (
        ("Agent", "Agent"),
        ("Merchant", "Merchant"),
    )

    NETWORKS = (
        ("Mtn", "Mtn"),
        ("Telecel", "Telecel"),
        ("AirtelTigo", "AirtelTigo"),
    )

    REQUEST_STATUS = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected")
    )
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_pay_to")
    network = models.CharField(max_length=20, choices=NETWORKS, blank=True, default="Select Network")
    agent_number = models.CharField(max_length=10, null=True, blank=True)
    # customer_name = models.CharField(max_length=30, blank=True)
    transfer_type = models.CharField(max_length=20, blank=True, choices=PAY_TO_DEPOSIT_TYPE)
    merchant_code = models.CharField(max_length=30, blank=True, default="")
    merchant_number = models.CharField(max_length=30, blank=True, default="")
    amount = models.DecimalField(max_digits=19, decimal_places=2, blank=True)
    reference = models.CharField(max_length=100, blank=True, default="")
    # charges = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    # agent_commission = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    date_deposited = models.DateField(auto_now_add=True)
    time_deposited = models.TimeField(auto_now_add=True)
    
    # @classmethod
    # def total_cash_for_customer(cls, agent):
    #     total = cls.objects.filter(agent=agent).aggregate(Sum('amount'))
    #     return total['amount__sum'] or 0
    
    # def save(self, *args, **kwargs):
    #     commission_amount = self.cash_received - self.amount
        
    #     # Save the CustomerCashIn instance
    #     super().save(*args, **kwargs)
        
    #     CashInCommission.objects.update_or_create(
    #         customer_cash_in=self, defaults={'amount': commission_amount} 
    #     )

    def __str__(self):
        return f"Pay To of GH¢{self.amount} on {self.network} by {self.agent.phone_number}"
    

class BranchReport(models.Model):
    branch = models.ForeignKey(Agent, on_delete=models.CASCADE)
    report = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Report from {self.branch.full_name}"