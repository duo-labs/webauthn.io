from email.policy import default
from django import forms


class UsernameForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100, required=True)


class RegistrationOptionsRequestForm(forms.Form):
    username = forms.CharField(required=True, max_length=64)
    require_user_verification = forms.BooleanField(required=False, initial=False)
    attestation = forms.ChoiceField(
        required=True,
        choices=[
            ("none", "None"),
            ("direct", "Direct"),
        ],
    )
    attachment = forms.ChoiceField(
        required=True,
        choices=[
            ("all", "All Supported"),
            ("cross_platform", "Cross-Platform"),
            ("platform", "Platform"),
        ],
    )
    algorithms = forms.MultipleChoiceField(
        required=True, choices=[("es256", "ES256"), ("rs256", "RS256")]
    )
