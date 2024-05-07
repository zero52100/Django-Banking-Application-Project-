

from django.core.mail import send_mail
from django.conf import settings

def send_balance_notification(account):
    if account.status == 'approved' and account.account_balance < account.account_variant.minimum_balance:
        subject = 'Account Balance Notification'
        message = f"Hello {account.user.full_name},\n\nYour account balance for account number {account.account_number} is below the minimum balance:₹{account.account_variant.minimum_balance}. Available Balance: ₹{account.account_balance}"
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [account.user.email]
        send_mail(subject, message, email_from, recipient_list)

def send_email(subject, message, recipient_list):
    
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, recipient_list)