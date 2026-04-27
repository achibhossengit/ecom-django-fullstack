from django import forms
from django.template.loader import render_to_string


class FancyFieldMixin:
    base_class = "w-full"

    input_class = "input input-bordered"
    email_class = "input input-bordered"
    select_class = "select select-bordered"
    checkbox_class = "checkbox"
    textarea_class = "textarea"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            widget = field.widget

            if isinstance(widget, forms.TextInput):
                css = self.input_class
            elif isinstance(widget, forms.EmailInput):
                css = self.email_class
            elif isinstance(widget, forms.Select):
                css = self.select_class
            elif isinstance(widget, forms.CheckboxInput):
                css = self.checkbox_class
            elif isinstance(widget, forms.Textarea):
                css = self.textarea_class
            elif isinstance(widget, forms.NumberInput):
                css = self.input_class
            else:
                css = ""
                

            existing = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{existing} {css} {self.base_class}".strip()

class FancyFormMixin:
    fancy_template = "core/forms/fancy_form.html"

    def as_fancy(self):
        return render_to_string(
            self.fancy_template,
            {"form": self}
        )
        
class FancyFormFieldMixin(FancyFieldMixin, FancyFormMixin):
    pass