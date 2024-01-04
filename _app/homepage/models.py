from typing import List, Optional

from pydantic import BaseModel
from webauthn.helpers.structs import AuthenticatorTransport, CredentialDeviceType


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
    is_discoverable_credential: Optional[bool]
    device_type: CredentialDeviceType
    backed_up: bool
    transports: Optional[List[AuthenticatorTransport]]
    # TODO: Clear this at some point point in the future when we know we're setting it
    aaguid: str = ""
