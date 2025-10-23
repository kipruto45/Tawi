import os
import sys
from django import forms

# Ensure DJANGO_SETTINGS_MODULE is set when the script is invoked directly
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tawi_project.settings')
import django
django.setup()

from django.template.loader import get_template


class F(forms.Form):
    beneficiary = forms.CharField(required=False)
    submitted_by = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea, required=False)


def render_check():
    try:
        t = get_template('feedback/submit_feedback.html')
        html = t.render({'form': F(), 'messages': []})
        print('TEMPLATE_RENDER_OK')
        print(html[:1000])
        return 0
    except Exception:
        import traceback
        traceback.print_exc()
        print('TEMPLATE_RENDER_ERROR')
        return 2


if __name__ == '__main__':
    sys.exit(render_check())
