from django import forms
from .models import File


class FileForm(forms.Form):
    # class Meta:
        model= File
        fields = ['file', 'Email']
    