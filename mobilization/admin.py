from django.contrib import admin
from .models import MobilizationPayTo, BankDeposit, BankWithdrawal, PaymentRequest, CustomerAccount, TellerCalculator

# Register your models here.
admin.site.register(MobilizationPayTo)
admin.site.register(BankDeposit)
admin.site.register(BankWithdrawal)
admin.site.register(PaymentRequest)
admin.site.register(CustomerAccount)
admin.site.register(TellerCalculator)