from django.urls import path
from .views import SavingsGoalCreateAPIView, SavingsGoalDetailsAPIView, SavingsGoalListAPIView

urlpatterns = [
    path('savings-goals/', SavingsGoalListAPIView.as_view(), name='savings-goal-list'),
    path('savings-goals/create/', SavingsGoalCreateAPIView.as_view(), name='savings-goal-create'),
    path('savings-goals/<int:pk>/', SavingsGoalDetailsAPIView.as_view(), name='savings-goal-details'),
]
