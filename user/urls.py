from django.urls import path
from .views import SignupView, SignInView, EmailVerifyView, EmailVerifyConfirmView, EmailVerifyDoneView, EmailVerifyCompleteView, EmailVerifyFailedView, SignUpWithGoogle, SignUpWithGoogleConfirm

urlpatterns = [
    path('signup/', SignupView.as_view(), name="signup"),
    path('signin/', SignInView.as_view(), name="signin"),
    path('email-verify/', EmailVerifyView.as_view(), name="email_verify"),
    path('email-verify/done', EmailVerifyDoneView.as_view(), name="email_verify_done"),
    path('email-verify/<uidb64>/<token>/', EmailVerifyConfirmView.as_view(), name="email_verify_confirm"),
    path('email-verify/complete', EmailVerifyCompleteView.as_view(), name="email_verify_complete"),
    path('email-verify/failed', EmailVerifyFailedView.as_view(), name="email_verify_failed"),
    path('signup/google/', SignUpWithGoogle.as_view(), name="signup_with_google"),
    path('signup/google/confirm/', SignUpWithGoogleConfirm.as_view(), name="signup_with_google_confirm"),
]
