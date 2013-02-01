from django import forms

class ClientRegForm(forms.Form):
    """docstring for ClientRegForm"""
    client_id = forms.CharField(max_length=128)
    name = forms.CharField(max_length=256)
    organization = forms.BooleanField()
