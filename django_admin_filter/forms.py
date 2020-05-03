from django import forms
from .models import Filter


class FilterForm(forms.ModelForm):
    name = forms.CharField(required=False)

    class Meta:
        model = Filter
        fields = ['name', 'description']
