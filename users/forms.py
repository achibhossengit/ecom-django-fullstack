from django import forms
from django.contrib.auth import get_user_model
from core.mixins import FancyFormFieldMixin
from .models import UserAddress

AuthUser = get_user_model()

class UserSignUpForm(FancyFormFieldMixin, forms.Form):
    first_name = forms.CharField(max_length=30, label="First Name", widget=forms.TextInput(attrs={"placeholder": "Enter your first name"}))
    last_name = forms.CharField(max_length=30, label="Last Name", widget=forms.TextInput(attrs={"placeholder": "Enter your last name"}))

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

class UserUpdateForm(FancyFormFieldMixin, forms.ModelForm):
    class Meta:
        model = AuthUser
        fields = ['username', 'first_name', 'last_name']
 
 
class UserAddressForm(FancyFormFieldMixin, forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = ['name', 'phone_number', 'description', 'type', 'country_id', 'city_id', 'area_id', 'zone_id']