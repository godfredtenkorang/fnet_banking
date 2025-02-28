from django.contrib import admin
from .models import CustomerCashIn, CustomerCashOut, BankWithdrawal

# Register your models here.
admin.site.register(CustomerCashIn)
admin.site.register(CustomerCashOut)
admin.site.register(BankWithdrawal)