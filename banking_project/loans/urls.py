# loans/urls.py

from django.urls import path
from .views import LoanTypeListCreateView,LoanTypeDetailUpdateDeleteView,LoanApplicationCreateView

urlpatterns = [
    path('loan-types/', LoanTypeListCreateView.as_view(), name='loan-type-list-create'),
    path('loan-types/<int:pk>/', LoanTypeDetailUpdateDeleteView.as_view(), name='loan-type-detail-update-delete'),
    path('loan-applications/', LoanApplicationCreateView.as_view(), name='loan-application-create'),
]
