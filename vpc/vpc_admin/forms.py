from django import forms

class ClientRegForm(forms.Form):
    """docstring for ClientRegForm"""
    client_id = forms.CharField(max_length=128, label="Client ID")
    name = forms.CharField(max_length=256, label="Full Name", required=True)
    email = forms.EmailField(required=True)
    organization = forms.BooleanField(label="Is Organization", required=False)
