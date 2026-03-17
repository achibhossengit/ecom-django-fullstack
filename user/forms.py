import logging
from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.forms import BaseUserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from .models import CustomUser

UserModel = get_user_model()
logger = logging.getLogger(__name__)

def send_verification_email(user, request):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    verification_link = request.build_absolute_uri(
        reverse("email_verify_confirm", kwargs={"uidb64": uidb64, "token": token})
    )    

    context = {
        "user": user,
        "link": verification_link,
    }
    text_content = "Please verify your email."
    subject = f"Verify Your Email"
    body = render_to_string("emails/verification_email.html", context)
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        to=[user.email],
    )
    email.attach_alternative(body, "text/html")
    email.send()    

class CustomUserCreationForm(BaseUserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})
            
    def save(self, request):
        user = super().save(commit=False)
        user.is_active = False
        user.email_verified = False
        user.save()
        
        try:
            send_verification_email(user, request)
        except Exception:
            logger.exception(f"Failed to send Verification Email to {user.pk}")
        return user

class EmailVerifyForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-input"
    }))
    
    def clean(self):
        email = self.cleaned_data["email"]
        user = UserModel.objects.get(email=email)
        if user and not user.is_active and not user.email_verified:
            self.user = user
            return super().clean()
        
        raise forms.ValidationError("No active user found with this email or email is already verified!")
    
    def save(self, request):
        user = self.user # set by clean method
        try:
            send_verification_email(user, request)
        except Exception:
            logger.exception(f"Failed to resend Verification Email to {user.pk}")        

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})
            
    def confirm_login_allowed(self, user):
        if not user.email_verified:
            raise ValidationError(
                "Account is not email verified.Check your inbox to verify first!",
                code="email_not_verified",
            )
        
        return super().confirm_login_allowed(user)
    