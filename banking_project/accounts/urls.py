from django.urls import path
from .views import BranchListCreateAPIView, BranchDetailAPIView,AccountTypeListCreateAPIView,AccountTypeDetailsAPIView,BankStaffListCreateAPIView,BankStaffDetailsAPIView,AccountCreateAPIView, AccountApprovalAPIView,AccountDetailsAPIView,DespositTypeListCreateAPIView,DepositTypeDetailsAPIView


urlpatterns = [
    path('branches/', BranchListCreateAPIView.as_view(), name='branch-create'),
    path('branches/<int:pk>/', BranchDetailAPIView.as_view(), name='branch-detail'),
    path('accountType/', AccountTypeListCreateAPIView.as_view(), name='accountType-create'),
    path('accountType/<int:pk>/', AccountTypeDetailsAPIView.as_view(), name='accountType-detail'),
    path('bankstaff/', BankStaffListCreateAPIView.as_view(), name='bankstaff-list-create'),
    path('bankstaff/<int:pk>/', BankStaffDetailsAPIView.as_view(), name='bankstaff-detail'),
    path('account/create/', AccountCreateAPIView.as_view(), name='account-create'),
    path('account/approve/<int:account_id>/', AccountApprovalAPIView.as_view(), name='account-approve'),
    path('account/<int:pk>/', AccountDetailsAPIView.as_view(), name='account-details'),
    path('depositType/', DespositTypeListCreateAPIView.as_view(), name='depositType-create'),
    path('depositType/<int:pk>/', DepositTypeDetailsAPIView.as_view(), name='depositType-detail'),
]
