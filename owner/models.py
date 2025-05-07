from django.db import models
from users.models import Owner

# Create your models here.
class OwnerBalance(models.Model):
    user = models.ForeignKey(Owner, on_delete=models.CASCADE)
    
    # Cash balances
    cash_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Telco balances
    mtn_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    telecel_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    airteltigo_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Bank balances
    ecobank_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    gtbank_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fidelity_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    calbank_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    absa_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    debtor_name1 = models.CharField(max_length=100, null=True, blank=True, default='')
    debtor_1_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    debtor_name2 = models.CharField(max_length=100, null=True, blank=True, default='')
    debtor_2_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    debtor_name3 = models.CharField(max_length=100, null=True, blank=True, default='')
    debtor_3_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    debtor_name4 = models.CharField(max_length=100, null=True, blank=True, default='')
    debtor_4_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    debtor_name5 = models.CharField(max_length=100, null=True, blank=True, default='')
    debtor_5_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Other fields
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name}'s Account Balances"