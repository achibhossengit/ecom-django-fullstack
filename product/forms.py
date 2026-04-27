from django import forms
from core.mixins import FancyFormFieldMixin
from .models import Product, Category


class CategoryModelForm(FancyFormFieldMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class ProductModelForm(FancyFormFieldMixin, forms.ModelForm):
    quantity = forms.IntegerField(min_value=0, initial=1)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'quantity', 'price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing product, populate fields from inventory
        if self.instance and hasattr(self.instance, "inventory"):
            self.fields["quantity"].initial = self.instance.inventory.quantity
            self.fields["price"].initial = self.instance.inventory.price