from django.contrib import admin
from .models import Bank, CustomerAccount, Drawer

# Register your models here.
admin.site.register(Bank)
admin.site.register(CustomerAccount)
admin.site.register(Drawer)