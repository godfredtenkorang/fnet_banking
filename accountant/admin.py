from django.contrib import admin

# Register your models here.
from .models import Transaction, TransactionCategory

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