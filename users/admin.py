from django.contrib import admin
from .models import User, Branch, Owner, Agent, Customer, Mobilization, Vehicle, Driver, MobilizationCustomer, Accountant, OTPToken
from django import forms


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'email', 'role', 'is_approved', 'is_blocked')
    list_editable = ('is_approved', 'is_blocked')  # Allow editing approval status directly from the list view
    list_filter = ('role', 'is_approved')
    actions = ['block_users', 'unblock_users']

    def block_users(self, request, queryset):
        queryset.update(is_blocked=True)
    block_users.short_description = "Block selected users"

    def unblock_users(self, request, queryset):
        queryset.update(is_blocked=False)
    unblock_users.short_description = "Unblock selected users"

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    list_filter = ('name',)

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('owner', 'branch')
    list_filter = ('owner',)
    
@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('driver', 'email', 'full_name')
    
@admin.register(Accountant)
class AccountantAdmin(admin.ModelAdmin):
    list_display = ('accountant', 'email', 'full_name')

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('agent', 'owner', 'branch')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer', 'agent', 'mobilization', 'branch')
    
@admin.register(Mobilization)
class MobilizationAdmin(admin.ModelAdmin):
    list_display = ('mobilization', 'owner', 'branch')
    
@admin.register(MobilizationCustomer)
class MobilizationCustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'mobilization', 'branch')
    


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    
    list_display = ('model', 'registration_number', 'oil_change_default', 'mileage_until_oil_change', 'needs_oil_change')
    list_filter = ('distance_unit', 'model')
    readonly_fields = ('mileage_until_oil_change', 'needs_oil_change')
    search_fields = ('registration_number', 'model')
    
    



admin.site.register(OTPToken)
