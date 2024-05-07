from django.urls import path
from .views import UserCreateView,VerifyOTPView,LoginView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('verify-otp/',VerifyOTPView.as_view(), name='verify-otp'),
    path('login/',LoginView.as_view(), name='user-login'),
]
