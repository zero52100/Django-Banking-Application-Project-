from django.urls import path
from .views import TransactionViewSet, CustomerTransferView


urlpatterns = [
    path('transaction/', TransactionViewSet.as_view(), name='transaction'),
    path('fundtransfer/',  CustomerTransferView.as_view(), name='fundtransfer')
    
]
