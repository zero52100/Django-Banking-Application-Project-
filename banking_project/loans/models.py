

from django.db import models
from accounts.models import Branch
from django.contrib.auth import get_user_model

User = get_user_model()

class LoanType(models.Model):
    LOAN_TYPES = [
        ('personal', 'Personal Loan'),
        ('home', 'Home Loan'),
        ('car', 'Car Loan'),
        ('education', 'Education Loan'),
    ]
    
    name = models.CharField(max_length=100, choices=LOAN_TYPES)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2)
    max_loan_amount = models.DecimalField(max_digits=15, decimal_places=2)
    min_loan_amount = models.DecimalField(max_digits=15, decimal_places=2)

class LoanApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_account_number = models.CharField(max_length=14, unique=True, null=True, blank=True)
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    status_choices = [
        ('applied', 'Applied'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='applied')
    created_at = models.DateTimeField(auto_now_add=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE,default=4)
    outstanding_balance = models.DecimalField(max_digits=15, decimal_places=2)


