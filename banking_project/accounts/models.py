from django.db import models
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

User = get_user_model()



class AccountType(models.Model):
    

    ACCOUNT_TYPES = [
        ('saving', 'Saving Account'),
        ('current', 'Current Account'),
    ]
    ACCOUNT_SUBTYPES = [
        ('saving-standard', 'Standard Saving Account'),
        ('saving-premium', 'Premium Saving Account'),
        ('current-standard', 'Standard Current Account'),
        ('current-premium', 'Premium Current Account'),
    ]
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_subtype = models.CharField(max_length=20, choices=ACCOUNT_SUBTYPES)
    
    minimum_balance = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    senior_citizen_interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_transaction_limit = models.IntegerField()
    
    additional_atm_charge = models.DecimalField(max_digits=5, decimal_places=2)
    debit_card_yearly_fee = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    free_atm_withdrawals = models.IntegerField()

class Branch(models.Model):
    bank_name = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=100)
    bank_manager = models.OneToOneField(User, on_delete=models.CASCADE, related_name='managed_branch', null=True, blank=True,unique=True)
    ifsc_code = models.CharField(max_length=11, unique=True)
    mobile_number = models.CharField(max_length=10)
    address = models.TextField()
    pincode = models.CharField(max_length=6)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_choices = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='inactive')

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=14, unique=True, null=True, blank=True)
    account_variant = models.ForeignKey(AccountType, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    debit_card_number = models.CharField(max_length=16, unique=True, null=True, blank=True)
    account_balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, default=0)
    status_choices = [
        ('applied', 'Applied'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='applied')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.id:
            
            if self.user.age > 60:
                self.interest_rate = self.account_variant.interest_rate + self.account_variant.senior_citizen_interest_rate
            else:
                self.interest_rate = self.account_variant.interest_rate

        super().save(*args, **kwargs)
class BankStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    designation_choices = [
        ('manager', 'Manager'),
        ('loan_officer', 'Loan Officer'),
        ('cashier', 'Cashier'),
    ]
    designation = models.CharField(max_length=20, choices=designation_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
       
        super(BankStaff, self).save(*args, **kwargs)

        
        if self.designation == 'manager':
            self.branch.bank_manager = self.user
            self.branch.save()
            if self.branch.status != 'active':
                self.branch.status = 'active'
                self.branch.save()

# Signal receiver to update branch's bank_manager when a BankStaff is saved
@receiver(post_save, sender=BankStaff)
def update_branch_manager(sender, instance, created, **kwargs):
    if created and instance.designation == 'manager':
        instance.branch.bank_manager = instance.user
        instance.branch.save()
        if instance.branch.status != 'active':
            instance.branch.status = 'active'
            instance.branch.save()
# Signal receiver to clear branch's bank_manager when a BankStaff is deleted
@receiver(post_delete, sender=BankStaff)
def clear_branch_manager(sender, instance, **kwargs):
    if instance.designation == 'manager':
        instance.branch.bank_manager = None
        instance.branch.save()



class Deposit(models.Model):
    DEPOSIT_TYPES = [
        ('FD', 'Fixed Deposit'),
        ('RD', 'Recurring Deposit'),
    ]
    
    deposit_type = models.CharField(max_length=2, choices=DEPOSIT_TYPES)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_deposit_type_display()} - {self.interest_rate}%"

class UserDeposit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deposit_type = models.ForeignKey(Deposit, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    current_value = models.DecimalField(max_digits=15, decimal_places=2)
    status_choices = [
        ('open', 'open'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='open')
    deposit_number =models.CharField(max_length=14, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.deposit} - {self.amount}"


@receiver(post_save, sender=UserDeposit)
def calculate_interest(sender, instance, created, **kwargs):
    if created:
        deposit_type = instance.deposit_type
        current_amount = instance.amount
        interest_rate = deposit_type.interest_rate
        
        # Calculate interest from creation to current time
        creation_date = instance.created_at.date()
        current_date = datetime.now().date()
        days_difference = (current_date - creation_date).days
        daily_interest_rate = interest_rate / 365
        interest = current_amount * daily_interest_rate * days_difference
        
        # Update the current value with interest
        instance.current_value = current_amount + interest
        instance.save()

        

        