from django import forms
from .models import File
from .models import PDF


class FileForm(forms.Form):
    file = forms.FileField(label='Select a file :)')
    

class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDF
        fields = ['name', 'file']