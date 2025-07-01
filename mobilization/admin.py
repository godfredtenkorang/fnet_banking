from django.contrib import admin
from .models import MobilizationPayTo, BankDeposit, BankWithdrawal, PaymentRequest, CustomerAccount, TellerCalculator, Report

# Register your models here.
admin.site.register(MobilizationPayTo)
admin.site.register(BankDeposit)
admin.site.register(BankWithdrawal)
admin.site.register(PaymentRequest)
@admin.register(CustomerAccount)
class CustomerAccountAdmin(admin.ModelAdmin):
    
    list_display = ('customer', 'account_number', 'account_name', 'bank', 'phone_number', 'date_added')
    list_filter = ('phone_number', 'account_number')
    search_fields = ('phone_number', 'account_number', 'account_name')
    
    
    
admin.site.register(TellerCalculator)
admin.site.register(Report)