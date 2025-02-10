# forms.py
from django import forms
from django.forms.widgets import ClearableFileInput

class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        final_attrs = {'multiple': True}
        if attrs:
            final_attrs.update(attrs)
        super().__init__(attrs=final_attrs)


class ImageUploadForm(forms.Form):
    images = forms.FileField(
        widget=MultiFileInput(),
        required=False
    )
    # Optional: If you want to attach images to an existing chat.
    chat_id = forms.IntegerField(required=True)