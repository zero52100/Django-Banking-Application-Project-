from django.urls import path
from .views import TransactionViewSet, CustomerTransferView,CustomerTransactionListView


urlpatterns = [
    path('transaction/', TransactionViewSet.as_view(), name='transaction'),
    path('fundtransfer/',  CustomerTransferView.as_view(), name='fundtransfer'),
    path('customer/transactions/', CustomerTransactionListView.as_view(), name='customer_transactions'),
    
]
