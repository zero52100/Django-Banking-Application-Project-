from django.urls import path
from .views import UserCreateView,VerifyOTPView,LoginView,LogoutAPIView,RequestPasswordResetView, VerifyOTPAndResetPasswordView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('verify-otp/',VerifyOTPView.as_view(), name='verify-otp'),
    path('login/',LoginView.as_view(), name='user-login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('password-reset/request/', RequestPasswordResetView.as_view(), name='request_password_reset'),
    path('password-reset/verify/', VerifyOTPAndResetPasswordView.as_view(), name='verify_otp_and_reset_password'),
]
