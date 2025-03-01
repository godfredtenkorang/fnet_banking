from django.contrib import admin
from .models import CustomerCashIn, CustomerCashOut, BankWithdrawal, CashAndECashRequest

# Register your models here.
admin.site.register(CustomerCashIn)
admin.site.register(CustomerCashOut)
admin.site.register(BankWithdrawal)
admin.site.register(CashAndECashRequest)