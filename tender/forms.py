from django import forms
from tender.models import OpenTendering


class DateInput(forms.DateInput):
    input_type = 'date'


class OpenTenderingForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'style': 'resize:none;'}))

    class Meta:
        model = OpenTendering
        exclude = ['contract_address']
        widgets = {
            'due_date': DateInput
        }
