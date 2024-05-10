from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction
from .serializers import TransactionSerializer
from accounts.models import Account, BankStaff
from django.core.mail import send_mail
from django.conf import settings
from utilities.notifications import send_balance_notification
from utilities.goal_checker import check_savings_goal_status
from authentication.Permissions.permission import check_blacklisted_access_token


class TransactionViewSet(APIView):

    def post(self, request):
        check_blacklisted_access_token(self.request)
        data = request.data
        user = request.user
        staff = BankStaff.objects.filter(user=user, designation='cashier').first()
        if staff:
            transaction_type = data.get('transaction_type')
            if transaction_type in ['deposit', 'withdrawal']:
                account_number = data.get('account_number')
                amount = data.get('amount')
                account = Account.objects.filter(account_number=account_number).first()
                if account:
                    if transaction_type == 'deposit':
                        transaction = Transaction(
                            user=account.user,
                            account=account,
                            transaction_type='deposit',
                            amount=amount,
                            
                            status='successful',
                            staff=staff
                        )
                        transaction.account_balance = account.account_balance + amount
                        
                        transaction.save()
                        send_balance_notification(account)

                        # Update the account balance after deposit
                        account.account_balance += amount
                        check_savings_goal_status(account.user)
                        account.save()
                        subject = 'Deposit Notification'
                        message = f"Hello {account.user.full_name},\n\nYour deposit transaction of ₹{amount} has been successful. \n Transaction ID: {transaction.transaction_number}"
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [account.user.email]
                        send_mail(subject, message, email_from, recipient_list)

                    elif transaction_type == 'withdrawal':
                        if account.account_balance >= amount:
                            transaction = Transaction(
                                user=user,
                                account=account,
                                transaction_type='withdrawal',
                                amount=amount,
                                status='successful',
                                staff=staff
                            )
                            transaction.account_balance = account.account_balance - amount
                            
                            transaction.save()

                            # Update the account balance after withdrawal 
                            account.account_balance -= amount
                            account.save()
                            subject = 'Withdrawal Notification'
                            message = f"Hello {account.user.full_name},\n\nYour withdrawal transaction of ₹{amount} has been successful. \n Transaction ID: {transaction.transaction_number}"
                            email_from = settings.EMAIL_HOST_USER
                            recipient_list = [account.user.email]
                            send_mail(subject, message, email_from, recipient_list)
                        else:
                            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    
                    serializer = TransactionSerializer(transaction)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': 'Invalid account number'}, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                return Response({'error': 'Invalid transaction type'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'User is not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)

class CustomerTransferView(APIView):
    
    def post(self, request):
        check_blacklisted_access_token(self.request)
        data = request.data
        user = request.user
        account_number = data.get('account_number')
        destination_account_number = data.get('destination_account_number')
        amount = data.get('amount')

        # Check if the user is authenticated and is a customer
        if request.user.is_authenticated and request.user.user_type == 'customer':
            # Retrieve the customer's account
            account = Account.objects.filter(user=user, account_number=account_number).first()
            if account:
                # Check if the account is approved
                if account.status == 'approved':
                    # Check if the destination account exists
                    destination_account = Account.objects.filter(account_number=destination_account_number).first()
                    if destination_account:
                        # Check if the source and destination accounts are different
                        if account_number != destination_account_number:
                            # Check if the transfer amount is valid
                            print("Transfer amount:", amount)
                            print("Account balance:", account.account_balance)
                            print("Type of amount:", type(amount))

                            if amount is not None and isinstance(amount, (int, float)) and amount > 0 and account.account_balance >= amount:
                                # Create a transaction for the source account (withdrawal)
                                transaction_withdrawal = Transaction.objects.create(
                                    user=user,
                                    account=account,
                                    transaction_type='transfer',
                                    amount=-amount,
                                    status='successful',
                                    staff=None,
                                    destination_account_number=destination_account_number,
                                    account_balance=account.account_balance - amount
                                )
                                # Update the source account balance
                                
                                account.account_balance -= amount
                                
                                account.save()
                                send_balance_notification(account)
                                sender_subject = 'Fund Transfer Notification'
                                sender_message = f"Hello {account.user.full_name},\n\nYou  transfer of ₹{amount} to  {destination_account.user.full_name} account {destination_account.account_number}. \n Avaliable balance: {account.account_balance}"
                                email_from = settings.EMAIL_HOST_USER
                                recipient_list = [account.user.email]
                                send_mail(sender_subject, sender_message, email_from, recipient_list)
                                

                                # Create a transaction for the destination account (deposit)
                                transaction_deposit = Transaction.objects.create(
                                    user=destination_account.user,
                                    account=destination_account,
                                    transaction_type='transfer',
                                    amount=amount,
                                    status='successful',
                                    staff=None,
                                    destination_account_number=account_number,
                                    account_balance=destination_account.account_balance + amount
                                )
                                # Update the destination account balance
                                destination_account.account_balance += amount
                                destination_account.save()
                                check_savings_goal_status(destination_account.user)
                                
                                send_balance_notification(destination_account)
                                # Send withdrawal notification to sender
                                receiver_subject = 'Fund Received Notification'
                                receiver_message = f"Hello {destination_account.user.full_name},\n\nYou received a transfer of ₹{amount} from {account.user.full_name} account {account_number}. \n Avaliable balance: {destination_account.account_balance}"
                                email_from = settings.EMAIL_HOST_USER
                                recipient_list = [account.user.email]
                                send_mail(receiver_subject, receiver_message, email_from, recipient_list)
                                serializer_withdrawal = TransactionSerializer(transaction_withdrawal)
                                serializer_deposit = TransactionSerializer(transaction_deposit)
                                return Response({
                                    'withdrawal_transaction': serializer_withdrawal.data,
                                    'deposit_transaction': serializer_deposit.data
                                }, status=status.HTTP_201_CREATED)
                            else:
                                return Response({'error': 'Invalid transfer amount or insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            return Response({'error': 'Source and destination accounts cannot be the same'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'error': 'Destination account does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': 'Account is not approved'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Invalid account number'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'User is not authenticated or not a customer'}, status=status.HTTP_403_FORBIDDEN)
        


