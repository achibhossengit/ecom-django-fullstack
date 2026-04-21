from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from core.mixins import FancyFieldMixin, FancyFormMixin

class UserSignUpForm(forms.Form):
    first_name = forms.CharField(max_length=30, label="First Name", widget=forms.TextInput(attrs={"placeholder": "Enter your first name"}))
    last_name = forms.CharField(max_length=30, label="Last Name", widget=forms.TextInput(attrs={"placeholder": "Enter your last name"}))

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

class UserUpdateForm(FancyFieldMixin, FancyFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']