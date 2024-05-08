from django.db import models
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
class Budget(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    monthly_budget = models.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Budget"

    def save(self, *args, **kwargs):
        # Calculate total expenses for the user
        total_expenses = Expense.objects.filter(user=self.user).aggregate(total=models.Sum('amount'))['total']
        if total_expenses is not None:
            self.total_expenses = total_expenses
        super().save(*args, **kwargs)

class Expense(models.Model):
    EXPENSE_CATEGORIES = [
        ('withdrawal', 'Withdrawal'),
        ('loan_repayment', 'Loan Repayment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100, choices=EXPENSE_CATEGORIES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - ${self.amount} on {self.date}"





