from django.contrib import admin
from .models import Bank, CustomerAccount, EFloatAccount, CustomerPaymentAtBank

# Register your models here.
admin.site.register(Bank)
admin.site.register(CustomerAccount)
admin.site.register(EFloatAccount)
admin.site.register(CustomerPaymentAtBank)