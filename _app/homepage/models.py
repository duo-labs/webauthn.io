from typing import List, Optional

from django.db import models
from pydantic import BaseModel
from webauthn.helpers.structs import AuthenticatorTransport


class TimestampedModel(models.Model):
    """
    A simple model subclass for adding created_on and updated_on fields
    """

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class WebAuthnCredential(BaseModel):
    """
    A Pydantic class for WebAuthn credentials in Redis. Includes information py_webauthn will need
    for verifying authentication attempts after registration.

    ID and public key bytes should be **Base64URL-encoded** for ease of storing in and referencing
    from Redis
    """

    id: str
    public_key: str
    username: str
    sign_count: int
    transports: Optional[List[AuthenticatorTransport]]
