from django.urls import path
from .views import SignupView, SignInView

urlpatterns = [
    path('signup/', SignupView.as_view(), name="signup"),
    path('signin/', SignInView.as_view(), name="signin"),
]
