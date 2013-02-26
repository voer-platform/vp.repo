from django import forms

class ClientRegForm(forms.Form):
    """docstring for ClientRegForm"""
    id = forms.IntegerField(widget=forms.HiddenInput)
    client_id = forms.CharField(max_length=128, label="Client ID",
                                help_text='Unique ID for each API client')
    name = forms.CharField(max_length=256, label="Full Name", required=True,
                                help_text='Name of the API client')
    email = forms.EmailField(required=True,
                                help_text='E-mail address of the API client')
    organization = forms.BooleanField(label="Is Organization", required=False)
    secret_key = forms.CharField(widget=forms.HiddenInput)
