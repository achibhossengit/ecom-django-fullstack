from django import forms
from django.contrib.auth.forms import BaseUserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(BaseUserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})
    