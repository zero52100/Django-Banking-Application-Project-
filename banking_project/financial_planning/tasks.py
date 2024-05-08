from celery import shared_task
from datetime import date
from django.contrib.auth import get_user_model
from .models import Budget

User = get_user_model()

@shared_task
def reset_remaining_budget():
    # Get all users with budgets
    users_with_budgets = User.objects.filter(budget__isnull=False)
    
    # Iterate through each user and update remaining budget
    for user in users_with_budgets:
        # Get the user's budget
        budget = Budget.objects.get(user=user)
        
        # Update remaining budget to be equal to the monthly budget
        budget.remaining_budget = budget.monthly_budget
        budget.save()
