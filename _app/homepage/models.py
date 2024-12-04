import json
from typing import List, Optional
from dataclasses import dataclass, asdict

from webauthn.helpers.structs import AuthenticatorTransport, CredentialDeviceType


@dataclass
class WebAuthnCredential:
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
    aaguid: str

    @classmethod
    def from_json(cls, cred_json: str | dict):
        """
        Parse a JSON-ified form of this class into a full-fat class
        """
        if type(cred_json) is str:
            _json: dict = json.loads(cred_json)
        elif type(cred_json) is dict:
            _json = cred_json
        else:
            raise Exception(f"Invalid type {type(cred_json)} for cred_json")

        transports_raw = _json.get("transports")
        transports_parsed = None
        if type(transports_raw) is list:
            transports_parsed = [AuthenticatorTransport(val) for val in transports_raw]

        return cls(
            id=_json["id"],
            public_key=_json["public_key"],
            username=_json["username"],
            sign_count=int(_json["sign_count"]),
            is_discoverable_credential=_json.get("is_discoverable_credential"),
            device_type=CredentialDeviceType(_json["device_type"]),
            backed_up=_json["backed_up"],
            transports=transports_parsed,
            aaguid=_json["aaguid"],
        )

    def to_json(self) -> dict:
        """
        Convert the model instance to a basic `dict`
        """
        return asdict(self)
