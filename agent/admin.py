from django.contrib import admin
from .models import CustomerCashIn, CustomerCashOut

# Register your models here.
admin.site.register(CustomerCashIn)
admin.site.register(CustomerCashOut)