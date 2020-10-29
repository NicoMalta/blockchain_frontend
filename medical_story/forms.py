from django import forms


class HistoryForm(forms.Form):
    diagnostic = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Diagnostic'}))
    dni = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder':'DNI'}))
    medicines = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Medicines'}))
    locality = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control form-control-user', 'placeholder': 'Locality'}))
