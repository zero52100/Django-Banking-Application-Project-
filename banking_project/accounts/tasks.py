
from celery import shared_task
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models import UserDeposit

@shared_task
def calculate_interest_and_update():
    # Get all open UserDeposit objects
    deposits = UserDeposit.objects.filter(status='open')
    
    # Calculate interest for each deposit
    for deposit in deposits:
        deposit_type = deposit.deposit_type
        current_value = deposit.current_value
        interest_rate = deposit_type.interest_rate
        
        # Calculate interest
        interest = (current_value * interest_rate) / 100
        
        # Update current value with interest
        deposit.current_value += interest
        deposit.save()