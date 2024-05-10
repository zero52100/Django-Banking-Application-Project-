from rest_framework.exceptions import PermissionDenied
from authentication.models import CustomsTokens

def check_blacklisted_access_token(request):
    access_token = request.auth
    if access_token and CustomsTokens.objects.filter(access_token=access_token, blacklisted=True).exists():
        raise PermissionDenied("Access token is blacklisted.")
