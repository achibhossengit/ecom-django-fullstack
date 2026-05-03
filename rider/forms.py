from django import forms
from core.mixins import FancyFormFieldMixin
from .models import RiderApplication


class RiderApplicationForm(FancyFormFieldMixin, forms.ModelForm):
    class Meta:
        model = RiderApplication
        fields = ["full_name", "nid_number", "vehicle_type", "license_number"]