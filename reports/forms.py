from django import forms


class CreateReportForm(forms.Form):
    name = forms.CharField(max_length=200)
    report_type = forms.ChoiceField(choices=[('summary','Summary'),('partner','Partner'),('public','Public')])
