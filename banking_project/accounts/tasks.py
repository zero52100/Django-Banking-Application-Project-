from .models import UserDeposit
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def calculate_interest_and_update():
    logger.info(f"Interest calculation started at {datetime.now()}")
    deposits = UserDeposit.objects.filter(status='open')
    
    for deposit in deposits:
        deposit_type = deposit.deposit_type
        current_value = deposit.current_value
        interest_rate = deposit_type.interest_rate
        print(interest_rate)
        interest = (current_value * interest_rate) / 100
        
        deposit.current_value += 3
        deposit.current_value += 3  # Adding 3 for testing purposes
        deposit.save()
        print(deposit.current_value)
    
    logger.info(f"Interest calculation completed at {datetime.now()}")
