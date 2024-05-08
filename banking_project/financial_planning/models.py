from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class SavingsGoal(models.Model):
    GOAL_STATUS_CHOICES = [
        ('processing', 'Goal Processing'),
        ('achieved', 'Goal Achieved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=100)
    goal_amount = models.DecimalField(max_digits=15, decimal_places=2)
    target_date = models.IntegerField()  # Number of months to achieve the goal
    created_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=GOAL_STATUS_CHOICES, default='processing')

    def __str__(self):
        return self.goal_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'processing':
            account_balance = self.user.account.account_balance
            
            if account_balance >= self.goal_amount:
                self.status = 'achieved'
                self.save()
                send_mail(
                    'Savings Goal Achieved',
                    f'Congratulations! Your savings goal "{self.goal_name}" has been achieved.',
                    settings.EMAIL_HOST_USER,
                    [self.user.email],
                    fail_silently=True,
                )
                print(account_balance)
class Budget(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    monthly_budget = models.DecimalField(max_digits=15, decimal_places=2)
    remaining_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Budget"

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - ${self.amount} on {self.date}"





