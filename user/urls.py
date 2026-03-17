from django.urls import path
from .views import SignupView, SignInView, EmailVerifyView, EmailVerifyConfirmView, EmailVerifyDoneView, EmailVerifyCompleteView, EmailVerifyFailedView

urlpatterns = [
    path('signup/', SignupView.as_view(), name="signup"),
    path('signin/', SignInView.as_view(), name="signin"),
    path('email-verify/', EmailVerifyView.as_view(), name="email_verify"),
    path('email-verify/done', EmailVerifyDoneView.as_view(), name="email_verify_done"),
    path('email-verify/<uidb64>/<token>/', EmailVerifyConfirmView.as_view(), name="email_verify_confirm"),
    path('email-verify/complete', EmailVerifyCompleteView.as_view(), name="email_verify_complete"),
    path('email-verify/failed', EmailVerifyFailedView.as_view(), name="email_verify_failed"),
]
