from django.urls import path
from .views import SavingsGoalCreateAPIView, SavingsGoalDetailsAPIView, SavingsGoalListAPIView,BudgetDetailsAPIView, ExpenseDetailsAPIView, BudgetCreateAPIView, ExpenseCreateAPIView   

urlpatterns = [
    path('savings-goals/', SavingsGoalListAPIView.as_view(), name='savings-goal-list'),
    path('savings-goals/create/', SavingsGoalCreateAPIView.as_view(), name='savings-goal-create'),
    path('savings-goals/<int:pk>/', SavingsGoalDetailsAPIView.as_view(), name='savings-goal-details'),
     path('budget/', BudgetCreateAPIView.as_view(), name='create_budget'),
    path('budget/<int:pk>/', BudgetDetailsAPIView.as_view(), name='budget_detail'),
    path('expense/', ExpenseCreateAPIView.as_view(), name='create_expense'),
    path('expense/<int:pk>/', ExpenseDetailsAPIView.as_view(), name='expense_detail'),
]
