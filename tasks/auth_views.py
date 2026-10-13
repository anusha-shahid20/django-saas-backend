from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.throttling import AnonRateThrottle


class LoginThrottle(AnonRateThrottle):
    """Custom throttle class for login endpoint."""
    scope = 'login'


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """
    Login endpoint with rate limiting.
    Limits anonymous users to 5 login attempts per minute.
    """
    throttle_classes = [LoginThrottle]