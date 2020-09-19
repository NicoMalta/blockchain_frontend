from django import forms
from login.models import BlockchainAccount


class BlockchainAccountForm(forms.ModelForm):
    class Meta:
        model = BlockchainAccount
        fields = ['address']
