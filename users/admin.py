from django.contrib import admin
from .models import User, Branch, Owner, Agent, Customer

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'is_approved', 'is_blocked')

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')

@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch')

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('user', 'owner', 'branch')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'agent', 'branch')