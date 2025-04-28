from django.contrib import admin
from .models import MileageRecord, FuelRecord, Expense

# Register your models here.
admin.site.register(MileageRecord)
admin.site.register(FuelRecord)
admin.site.register(Expense)