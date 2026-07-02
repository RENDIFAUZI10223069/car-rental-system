from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import AdminLoginView

urlpatterns = [
    path("login/", AdminLoginView.as_view(), name="admin-login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
]
