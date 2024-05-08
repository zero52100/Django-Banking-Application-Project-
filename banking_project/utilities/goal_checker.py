

from django.core.mail import send_mail
from django.conf import settings
from financial_planning.models import SavingsGoal

def check_savings_goal_status(user_id):
    # Retrieve the user's savings goals
    savings_goals = SavingsGoal.objects.filter(user_id=user_id, status='processing')

    # Iterate through the user's savings goals
    for savings_goal in savings_goals:
        account_balance = savings_goal.user.account.account_balance
        
        if account_balance >= savings_goal.goal_amount:
            savings_goal.status = 'achieved'
            savings_goal.save()
            send_mail(
                'Savings Goal Achieved',
                f'Congratulations! Your savings goal "{savings_goal.goal_name}" has been achieved.',
                settings.EMAIL_HOST_USER,
                [savings_goal.user.email],
                fail_silently=True,
            )
            print(account_balance)