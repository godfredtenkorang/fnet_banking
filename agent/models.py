from django.db import models
from django.conf import settings

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
    ("Approved", "Approved"),
    ("Pending", "Pending"),
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
    

