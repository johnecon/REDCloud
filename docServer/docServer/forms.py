from django import forms
from form_utils.fields import ClearableFileField

from docServer.models.project import *


class ResourceForm(forms.ModelForm):
    file = ClearableFileField()

    class Meta:
        model = Resource
        fields = ['name', 'file']