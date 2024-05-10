# loans/urls.py

from django.urls import path
from .views import LoanTypeListCreateView,LoanTypeDetailUpdateDeleteView,LoanApplicationCreateView,LoanApprovalAPIView,CustomerLoanStatusListView,LoanApplicationBranchListView

urlpatterns = [
    path('loan-types/', LoanTypeListCreateView.as_view(), name='loan-type-list-create'),
    path('loan-types/<int:pk>/', LoanTypeDetailUpdateDeleteView.as_view(), name='loan-type-detail-update-delete'),
    path('loan-applications/', LoanApplicationCreateView.as_view(), name='loan-application-create'),
    path('approve-or-reject-loan/', LoanApprovalAPIView.as_view(), name='approve_or_reject_loan'),
    path('customer/loans/status/', CustomerLoanStatusListView.as_view(), name='customer_loan_status_list'),
    path('loan-offcier/loans/status/', LoanApplicationBranchListView.as_view(), name='loan_offcer_view'),
]

