from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth.models import User
from .models import UserProfile

class LoginThrottle(AnonRateThrottle):
    """Custom throttle class for login endpoint."""
    scope = 'login'

class ThrottledTokenObtainPairView(TokenObtainPairView):
    """
    Login endpoint with rate limiting.
    Also returns the user's role upon successful login.
    """
    throttle_classes = [LoginThrottle]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
                profile = UserProfile.objects.get(user=user)
                # Add the user's role to the response so the frontend knows what to display
                response.data['role'] = profile.role
            except Exception:
                # Fallback if profile doesn't exist
                response.data['role'] = 'employee' 
                
        return response