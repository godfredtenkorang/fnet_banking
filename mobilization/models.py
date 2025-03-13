from django.db import models
from users.models import User, Mobilization
from django.utils import timezone
from django.db.models import Sum
from users.models import MobilizationCustomer, Customer

REQUEST_STATUS = (
    ("Pending", "Pending"),
    ("Approved", "Approved"),
    ("Rejected", "Rejected")
)

# Create your models here.

class MobilizationPayTo(models.Model):
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
    mobilization = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mobilization_pay_to")
    agent_number = models.CharField(max_length=10, blank=True)
    network = models.CharField(max_length=20, choices=NETWORKS, blank=True, default="Select Network")
    # customer_name = models.CharField(max_length=30, blank=True)
    deposit_type = models.CharField(max_length=20, blank=True, choices=PAY_TO_DEPOSIT_TYPE)
    sent_to_agent_number = models.CharField(max_length=30, blank=True, default="")
    merchant_code = models.CharField(max_length=30, blank=True, default="")
    merchant_number = models.CharField(max_length=30, blank=True, default="")
    amount = models.DecimalField(max_digits=19, decimal_places=2, blank=True)
    reference = models.CharField(max_length=100, blank=True, default="")
    # charges = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    # agent_commission = models.DecimalField(max_digits=19, decimal_places=2, default=0.0)
    date_deposited = models.DateField(auto_now_add=True)
    time_deposited = models.TimeField(auto_now_add=True)
    
    @classmethod
    def total_cash_for_customer(cls, mobilization):
        total = cls.objects.filter(mobilization=mobilization).aggregate(Sum('amount'))
        return total['amount__sum'] or 0
    
    # def save(self, *args, **kwargs):
    #     commission_amount = self.cash_received - self.amount
        
    #     # Save the CustomerCashIn instance
    #     super().save(*args, **kwargs)
        
    #     CashInCommission.objects.update_or_create(
    #         customer_cash_in=self, defaults={'amount': commission_amount} 
    #     )

    def __str__(self):
        return f"Pay To of GH¢{self.amount} on {self.network} by {self.mobilization}"
    
    
class BankDeposit(models.Model):
    mobilization = models.ForeignKey(Mobilization, on_delete=models.CASCADE, related_name='bank_deposits')
    phone_number = models.CharField(max_length=10)
    bank = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=100, choices=REQUEST_STATUS, default='Pending')
    date_deposited = models.DateField(default=timezone.now)
    time_deposited = models.TimeField(default=timezone.now)
    
    @classmethod
    def total_bank_deposit_for_customer(cls, mobilization):
        total = cls.objects.filter(mobilization=mobilization).aggregate(Sum('amount'))
        return total['amount__sum'] or 0
    
    def __str__(self):
        return f"Bank Deposit of GH¢{self.amount} to {self.bank} by {self.phone_number} ({self.status})"
    
class BankWithdrawal(models.Model):
    mobilization = models.ForeignKey(Mobilization, on_delete=models.CASCADE, related_name='bank_withdrawals')
    customer_phone = models.CharField(max_length=15)
    bank = models.CharField(max_length=20)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_withdrawn = models.DateField(default=timezone.now)
    time_withdrawn = models.TimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='Pending')
    
    @classmethod
    def total_bank_withdrawal_for_customer(cls, mobilization):
        total = cls.objects.filter(mobilization=mobilization).aggregate(Sum('amount'))
        return total['amount__sum'] or 0
    
    def __str__(self):
        return f"Bank Withdrawal of GH¢{self.amount} from {self.bank} by {self.customer_phone} ({self.status})"
    

class PaymentRequest(models.Model):
    MODE_OF_PAYMENT = [
        ('Telco', 'Telco'),
        ('Bank', 'Bank'),
        ('Branch', 'Branch'),
    ]
    
    BANK_CHOICES = [
        ("Select bank", "Select bank"),
        ("Ecobank", "Ecobank"),
        ("Access Bank", "Access Bank"),
        ("Cal Bank", "Cal Bank"),
        ("Fidelity Bank", "Fidelity Bank"),
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
    mobilization = models.ForeignKey(Mobilization, on_delete=models.CASCADE, related_name='payments_requests')
    mode_of_payment = models.CharField(max_length=10, choices=MODE_OF_PAYMENT, null=True, blank=True)
    bank = models.CharField(max_length=50, choices=BANK_CHOICES, null= True, blank=True)
    network = models.CharField(max_length=30, choices=NETWORK_CHOICES, null= True, blank=True)
    branch = models.CharField(max_length=30, choices=BRANCHES, null= True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    @classmethod
    def total_payment_for_customer(cls, mobilization):
        total = cls.objects.filter(mobilization=mobilization).aggregate(Sum('amount'))
        return total['amount__sum'] or 0
    
    def __str__(self):
        return f"Payment of ${self.amount} via {self.mode_of_payment} by {self.mobilization.user} ({self.status})"
    
    
class CustomerAccount(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customeraccounts')
    account_number = models.CharField(max_length=16, blank=True)
    account_name = models.CharField(max_length=100, blank=True)
    bank = models.CharField(max_length=100, blank=True, default='')
    phone_number = models.CharField(max_length=15, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.phone_number
    
    
class TellerCalculator(models.Model):
    mobilization = models.ForeignKey(Mobilization, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=13)
    amount = models.DecimalField(decimal_places=2, max_digits=19, default=0.0)
    d_200 = models.CharField(max_length=100, null=True, blank=True)
    d_100 = models.CharField(max_length=100, null=True, blank=True)
    d_50 = models.CharField(max_length=100, null=True, blank=True)
    d_20 = models.CharField(max_length=100, null=True, blank=True)
    d_10 = models.CharField(max_length=100, null=True, blank=True)
    d_5 = models.CharField(max_length=100, null=True, blank=True)
    d_2 = models.CharField(max_length=100, null=True, blank=True)
    d_1 = models.CharField(max_length=100, null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)
    time_added = models.TimeField(auto_now_add=True)
    

        
    def __str__(self):
        return f"{self.customer_name} - Total: {self.amount}"