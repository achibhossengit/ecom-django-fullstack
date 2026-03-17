from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, EmailVerifyForm, CustomAuthenticationForm
from .models import CustomUser


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
        print(f"Form is invalid for: {form.errors}")
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

