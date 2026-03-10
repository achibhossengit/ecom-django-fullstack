from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import BaseUserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(BaseUserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})

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
    