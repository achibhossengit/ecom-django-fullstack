import logging
import requests
from google_auth_oauthlib.flow import Flow
from oauthlib.oauth2 import OAuth2Error
from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy, reverse
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib import messages

from .forms import CustomUserCreationForm, EmailVerifyForm, CustomAuthenticationForm
from .models import CustomUser

logger = logging.getLogger(__name__)

class LoginNotRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("homepage")
        return super().dispatch(request, *args, **kwargs)

class SignupView(LoginNotRequiredMixin, FormView):
    form_class = CustomUserCreationForm
    template_name = "signup.html"
    success_url = reverse_lazy("email_verify_done")

    def form_valid(self, form):
        form.save(self.request)
        return super().form_valid(form)

class EmailVerifyView(LoginNotRequiredMixin, FormView):
    """
    Resend verification email.
    """
    form_class = EmailVerifyForm
    template_name = "email_verify_form.html"
    success_url = reverse_lazy("email_verify_done")
    
    def form_invalid(self, form):
        return super().form_invalid(form)
    
    def form_valid(self, form):
        form.save(self.request)
        return super().form_valid(form)
    
class EmailVerifyConfirmView(LoginNotRequiredMixin, View):
    def get_user(self, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except:
            user = None
        return user

    def get(self, request, uidb64, token, *args, **kwargs):
        user = self.get_user(uidb64)
        
        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.email_verified = True
            user.save()

            # login method update the "last_login" fields, which invalided this token.
            login(request, user)
            return redirect("email_verify_complete")

        return redirect("email_verify_failed")

class EmailVerifyDoneView(LoginNotRequiredMixin, TemplateView):
    template_name = "emails/email_verify_done.html"

class EmailVerifyCompleteView(TemplateView):
    template_name = "emails/email_verify_complete.html"

class EmailVerifyFailedView(LoginNotRequiredMixin, TemplateView):
    template_name = "emails/email_verify_failed.html"

    
class SignInView(LoginNotRequiredMixin, LoginView):
    form_class = CustomAuthenticationForm
    template_name = "signin.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('homepage')

class SignUpWithGoogle(View):
    """
    View to redirect google consent page with Credentials.
    """
    def get(self, request, *args, **kwargs):
        flow = Flow.from_client_config(
            client_config=settings.GOOGLE_CLIENT_CONFIG,
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile"
            ],
        )

        flow.redirect_uri = request.build_absolute_uri(
            reverse('signup_with_google_confirm')
        )
        
        authorization_url, state = flow.authorization_url()
        code_verifier = flow.code_verifier

        # save state + PKCE verifier
        request.session['oauth_state'] = state
        request.session['code_verifier'] = code_verifier
        
        return redirect(authorization_url)
    

class SignUpWithGoogleConfirm(View):
    def get(self, request, *args, **kwargs):
        """
        1. Collect state and authorization code.
        2. Verify state to protect against CSRF.
        3. Fetch auth token using auth code.
        4. Fetch user info using token.
        5. Create or get user in Django and log them in.
        """

        # state validation
        state = request.GET.get("state")

        if not state or state != request.session.get("oauth_state"):
            messages.error(request, "Invalid session. Please try again.")
            return redirect("/signin/")

        # authorization code check
        if "code" not in request.GET:
            messages.error(request, "Google login cancelled.")
            return redirect("/signin/")

        try:

            flow = Flow.from_client_config(
                client_config=settings.GOOGLE_CLIENT_CONFIG,
                scopes=[
                    "openid",
                    "https://www.googleapis.com/auth/userinfo.email",
                    "https://www.googleapis.com/auth/userinfo.profile"
                ],
                state=state
            )

            # restore PKCE
            code_verifier = request.session.get("code_verifier")

            if not code_verifier:
                messages.error(request, "Session expired. Try again.")
                return redirect("/signin/")

            flow.code_verifier = code_verifier

            flow.redirect_uri = request.build_absolute_uri(
                reverse("signup_with_google_confirm")
            )

            # exchange code for token
            flow.fetch_token(
                authorization_response=request.build_absolute_uri()
            )

            # get user info
            oauth_session = flow.authorized_session()

            resp = oauth_session.get(
                "https://openidconnect.googleapis.com/v1/userinfo"
            )

            if resp.status_code != 200:
                messages.error(request, "Failed to fetch user info.")
                return redirect("/signin/")

            user_info = resp.json()

            email = user_info.get("email")
            name = user_info.get("name")

            if not email:
                messages.error(request, "Email permission required.")
                return redirect("/signin/")

            # create user
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": name or ""
                }
            )
            user.email_verified = True
            user.save()

            # login
            login(request, user)

            # cleanup session
            request.session.pop("oauth_state", None)
            request.session.pop("code_verifier", None)

            return redirect("/")

        except OAuth2Error as e:

            # common OAuth issues
            logger.error("OAuth error:", e)

            messages.error(
                request,
                "Authentication failed. Please try again."
            )

            return redirect("/signin/")

        except requests.RequestException as e:

            # network error
            logger.error("Network error:", e)

            messages.error(
                request,
                "Connection problem with Google."
            )

            return redirect("/signin/")

        except Exception as e:

            # fallback
            logger.error("Unexpected error:", e)

            messages.error(
                request,
                "Unexpected error occurred."
            )

            return redirect("/signin/")