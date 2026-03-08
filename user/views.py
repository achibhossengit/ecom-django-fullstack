from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.views import LoginView


# Create your views here.
class SignupView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "signup.html"
    success_url = reverse_lazy("signin")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("homepage")
        return super().dispatch(request, *args, **kwargs)
    
class SignInView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "signin.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('homepage')

