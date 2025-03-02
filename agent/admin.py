from django.contrib import admin
from .models import CustomerCashIn, CustomerCashOut, BankDeposit, BankWithdrawal, CashAndECashRequest, PaymentRequest, CustomerComplain, HoldCustomerAccount, CustomerFraud

# Register your models here.
admin.site.register(CustomerCashIn)
admin.site.register(CustomerCashOut)
admin.site.register(BankDeposit)
admin.site.register(BankWithdrawal)
admin.site.register(CashAndECashRequest)
admin.site.register(PaymentRequest)
admin.site.register(CustomerComplain)
admin.site.register(HoldCustomerAccount)
admin.site.register(CustomerFraud)