from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from apps.authentication.apis.auth import VerifyOTPView, LoginView

urlpatterns = [
        path('jwt/', include(([
            path('login/', LoginView.as_view(),name="login"),
            path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
            path('refresh/', TokenRefreshView.as_view(),name="refresh"),
        ])), name="jwt"),
]
