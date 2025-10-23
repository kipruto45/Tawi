from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    def clean_role(self):
        """Normalize submitted role aliases to canonical role values.

        Some parts of the app historically use 'field' as an alias for
        'field_officer' and 'partner_institution' may be used for 'partner'.
        Normalize these to the canonical values used in redirect logic.
        """
        role = self.cleaned_data.get('role')
        mapping = {
            'field': 'field_officer',
            'partner_institution': 'partner',
        }
        return mapping.get(role, role)

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone', 'organization', 'county', 'ward', 'profile_picture')
