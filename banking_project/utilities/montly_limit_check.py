from datetime import datetime
from django.utils import timezone  # Importing Django's timezone module
from transactions.models import Transaction
from django.db import models

def calculate_total_transactions(user):
    # Calculate total withdrawals and deposits for the user from the 1st of the current month to the current date
    start_date = timezone.now().replace(day=1)  # Using timezone.now() instead of datetime.now()
    end_date = timezone.now()
    withdrawals = Transaction.objects.filter(
        user=user,
        transaction_type='withdrawal',
        transaction_date__gte=start_date,
        transaction_date__lte=end_date
    ).aggregate(total_withdrawals=models.Sum('amount'))['total_withdrawals'] or 0

    deposits = Transaction.objects.filter(
        user=user,
        transaction_type='deposit',
        transaction_date__gte=start_date,
        transaction_date__lte=end_date
    ).aggregate(total_deposits=models.Sum('amount'))['total_deposits'] or 0

    return withdrawals, deposits

def check_transaction_limit(user, amount):
    # Calculate total withdrawals and deposits
    total_withdrawals, total_deposits = calculate_total_transactions(user)

    # Check if transaction limit is exceeded for the account type
    account_type = user.account.account_variant
    print(account_type)
    monthly_limit = account_type.monthly_transaction_limit
    print(monthly_limit)
    total_transactions_this_month = total_withdrawals + total_deposits
    print(total_transactions_this_month)

    if total_transactions_this_month + 1 > monthly_limit:
        
        return False, f"Transaction limit ({monthly_limit}) exceeded for this account type for this month."
    if total_transactions_this_month + amount > monthly_limit:
        
        return False, f"Transaction limit ({monthly_limit}) exceeded for this account type for this month."
        

    

    return True, None
