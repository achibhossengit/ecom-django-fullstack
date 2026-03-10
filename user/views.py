from django.views import View
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser


# Create your views here.
class SignupView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "signup.html"
    success_url = reverse_lazy("signin")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("homepage")
        return super().dispatch(request, *args, **kwargs)

    def _send_verify_email(self, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        verification_link = self.request.build_absolute_uri(f"/verify-email/{uid}/{token}/")
        context = {
            "user": user,
            "link": verification_link,
        }
        html_content = render_to_string("emails/verification_email.html", context)
        text_content = "Please verify your email."
        email = EmailMultiAlternatives(
            subject="Verify Your Email",
            body=text_content,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.email_verified = False
        user.save()

        try:
            self._send_verify_email(user)
        except Exception as e:
            print(f"Email send failed for {user.email} with error {e}")

        return render(self.request, "emails/verification_email_send.html")
    
class VerifyEmailView(View):
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
            return render(request, "emails/verification_success.html")

        return render(request, "emails/verification_failed.html")
    
class SignInView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "signin.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('homepage')

