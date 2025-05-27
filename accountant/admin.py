from django.contrib import admin

# Register your models here.
from .models import Transaction, TransactionCategory, Vehicle, Branch

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'transaction_type', 'amount', 'date', 'created_by')
    list_filter = ('transaction_type', 'date')
    search_fields = ('transaction_id',)
    readonly_fields = ('created_by', 'created_at')

@admin.register(TransactionCategory)
class TransactionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_income')
    list_filter = ('is_income',)
    
@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('year', 'name', 'registration_number')
    list_filter = ('name',)
    
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name',)