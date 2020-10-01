from django import forms
from login.models import BlockchainAccount


class BlockchainAccountForm(forms.ModelForm):
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 6,
                                                           'cols': 22,
                                                           'style': 'resize:none;',
                                                           'readonly': 'readonly'}))

    class Meta:
        model = BlockchainAccount
        fields = ['address']
