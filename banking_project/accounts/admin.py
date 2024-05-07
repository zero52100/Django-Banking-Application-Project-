from django.contrib import admin
from .models import AccountType, Branch, Account, BankStaff



@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'account_type', 'account_subtype', 'minimum_balance', 'created_at', 'updated_at',
                    'interest_rate', 'senior_citizen_interest_rate', 'monthly_transaction_limit',
                ]

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['id', 'bank_name', 'branch_name', 'bank_manager', 'ifsc_code', 'mobile_number', 'status', 'created_at', 'updated_at']
    list_filter = ['status']
    search_fields = ['bank_name', 'branch_name', 'mobile_number']

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'account_number', 'account_variant', 'branch', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'account_variant']
    search_fields = ['user__username', 'account_number']

@admin.register(BankStaff)
class BankStaffAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'branch', 'designation', 'created_at', 'updated_at']
    list_filter = ['designation']
    search_fields = ['user__username', 'branch__branch_name']

