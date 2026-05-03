from django import forms
from core.mixins import FancyFormFieldMixin
from .models import RiderApplication


class RiderApplicationForm(FancyFormFieldMixin, forms.ModelForm):
    class Meta:
        model = RiderApplication
        fields = ["full_name", "nid_number", "vehicle_type", "license_number"]
        

# =====================
# Manager related forms
# ======================
class RiderApplicationStatusForm(forms.ModelForm):
    """Used by the manager to accept or reject an application."""

    class Meta:
        model = RiderApplication
        fields = ["status"]
        widgets = {"status": forms.HiddenInput()}