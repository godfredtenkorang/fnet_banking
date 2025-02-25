from django.db import models
from users.models import Customer, Agent
from django.utils import timezone

BANKS = (
    ("Select bank", "Select bank"),
    ("Access Bank", "Access Bank"),
    ("Cal Bank", "Cal Bank"),
    ("Fidelity Bank", "Fidelity Bank"),
    ("Ecobank", "Ecobank"),
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
    ("GT Bank", "GT Bank"),
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
)

class Bank(models.Model):
    name = models.CharField(max_length=100, choices=BANKS, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name
    
class CustomerAccount(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=16, blank=True)
    account_name = models.CharField(max_length=100, blank=True)
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.phone_number
    
class Drawer(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='drawers')
    date = models.DateField(default=timezone.now)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    closing_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_closed = models.BooleanField(default=False)
    
    
    def __str__(self):
        return f"Drawer from {self.agent.user.username} on {self.date}"
    
    