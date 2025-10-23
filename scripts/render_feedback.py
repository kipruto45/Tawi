from django import forms
from django.template.loader import get_template

class F(forms.Form):
    beneficiary = forms.CharField(required=False)
    submitted_by = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea, required=False)

try:
    t = get_template('feedback/submit_feedback.html')
    html = t.render({'form': F(), 'messages': []})
    print('TEMPLATE_RENDER_OK')
    # print a small prefix so output isn't huge
    print(html[:1000])
except Exception as e:
    import traceback
    traceback.print_exc()
    print('TEMPLATE_RENDER_ERROR:', e)
