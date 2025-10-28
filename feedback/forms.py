from django import forms
from .models import Feedback
from beneficiaries.models import Beneficiary


class FeedbackForm(forms.ModelForm):
    beneficiary = forms.ModelChoiceField(queryset=Beneficiary.objects.all(), required=False)

    class Meta:
        model = Feedback
        fields = ['beneficiary', 'submitted_by', 'email', 'phone', 'message']
        widgets = {
            'beneficiary': forms.Select(attrs={'class': 'w-full p-2 border border-green-300 rounded focus:ring-2 focus:ring-green-500 mb-3'}),
            'submitted_by': forms.TextInput(attrs={'class': 'w-full p-2 border border-green-300 rounded focus:ring-2 focus:ring-green-500 mb-3'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-2 border border-green-300 rounded focus:ring-2 focus:ring-green-500 mb-3'}),
            'phone': forms.TextInput(attrs={'class': 'w-full p-2 border border-green-300 rounded focus:ring-2 focus:ring-green-500 mb-3'}),
            'message': forms.Textarea(attrs={'rows': 5, 'class': 'w-full p-3 border border-green-300 rounded-md focus:ring-2 focus:ring-green-500 min-h-[100px] resize-y mb-4'}),
        }
