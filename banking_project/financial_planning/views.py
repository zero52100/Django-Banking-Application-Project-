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