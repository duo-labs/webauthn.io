from django.conf import settings
from django.db import models


class TimestampedModel(models.Model):
    """
    A simple model subclass for adding created_on and updated_on fields
    """

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class WebAuthnCredential(TimestampedModel):
    """
    A class for storying WebAuthn credentials. Includes information py_webauthn will need for
    verifying authentication attempts after registration.
    """

    id = models.BinaryField(primary_key=True)
    public_key = models.BinaryField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    sign_count = models.IntegerField()
    # "usb,nfc,ble,internal,cable" = 26 + buffer
    transports = models.CharField(max_length=32)

    class Meta:
        indexes = [
            models.Index(fields=["id"], name="credential_id_idx"),
            models.Index(fields=["user"], name="credential_user_idx"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["id", "user"], name="unique_credential_user")
        ]
