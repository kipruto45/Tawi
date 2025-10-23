from django import forms
from .models import Feedback
from beneficiaries.models import Beneficiary


class FeedbackForm(forms.ModelForm):
    beneficiary = forms.ModelChoiceField(queryset=Beneficiary.objects.all(), required=False)

    class Meta:
        model = Feedback
        fields = ['beneficiary', 'submitted_by', 'email', 'phone', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }
