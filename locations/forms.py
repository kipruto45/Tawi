from django import forms
from beneficiaries.models import PlantingSite, Beneficiary


class PlantingSiteForm(forms.ModelForm):
    class Meta:
        model = PlantingSite
        fields = ['beneficiary', 'name', 'address', 'latitude', 'longitude', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # make beneficiary selection clearer in admin forms
        self.fields['beneficiary'].queryset = Beneficiary.objects.all().order_by('name')
