from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import AdminTokenObtainPairSerializer


class AdminLoginView(TokenObtainPairView):
    """
    POST /api/v1/auth/login/
    body: { "username": "admin", "password": "admin12345" }
    """
    serializer_class = AdminTokenObtainPairSerializer
