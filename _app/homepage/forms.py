from django import forms


class UsernameForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100, required=True)
