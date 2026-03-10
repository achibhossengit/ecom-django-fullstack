from django.urls import path
from .views import SignupView, SignInView, VerifyEmailView

urlpatterns = [
    path('signup/', SignupView.as_view(), name="signup"),
    path('signin/', SignInView.as_view(), name="signin"),
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name="verify_email"),
]
