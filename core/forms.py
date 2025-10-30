from django import forms
from .models import Partner


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ['name', 'contact_name', 'contact_email', 'address']
