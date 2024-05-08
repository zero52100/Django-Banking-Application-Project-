from django.urls import path
from .views import SavingsGoalCreateAPIView

urlpatterns = [
    path('savings-goals/create/', SavingsGoalCreateAPIView.as_view(), name='create_savings_goal'),
]
