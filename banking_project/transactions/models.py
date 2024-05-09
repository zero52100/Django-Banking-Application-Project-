import uuid
from django.db import models
from accounts.models import Account,BankStaff
from django.contrib.auth import get_user_model

User = get_user_model()



class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('loan_repayment', 'Loan Repayment'),
        ('processing_fee','Processing Fee'),
        ('loan sactioned','Loan Sactioned'),
        ('deposit_creation','FD/RD Creation'),
        ('deposit_clouser','FD/RD Clouser')
        
    ]

    STATUS_CHOICES = [
        ('successful', 'Successful'),
        ('rejected', 'Rejected')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    destination_account_number = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='successful')
    transaction_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    staff = models.ForeignKey(BankStaff, on_delete=models.SET_NULL, null=True, blank=True)
    account_balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=None)

    