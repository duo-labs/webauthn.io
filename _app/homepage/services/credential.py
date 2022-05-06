from typing import List, Optional
import json

from webauthn.registration.verify_registration_response import VerifiedRegistration
from webauthn.helpers import bytes_to_base64url

from homepage.services.redis import RedisService
from homepage.models import WebAuthnCredential
from homepage.exceptions import InvalidCredentialID


class CredentialService:
    """
    WebAuthn credential management
    """

    redis: RedisService

    def __init__(self) -> None:
        self.redis = RedisService(db=0)

    def store_credential(
        self,
        *,
        username: str,
        registration: VerifiedRegistration,
        transports: Optional[List[str]] = None
    ) -> WebAuthnCredential:
        """
        Temporarily store a new credential in Redis so we can leverage its record expiration to
        remove credentials after a certain number of hours

        The Redis key will be the base64url-encoded credential ID
        """
        new_credential = WebAuthnCredential(
            username=username,
            id=bytes_to_base64url(registration.credential_id),
            public_key=bytes_to_base64url(registration.credential_public_key),
            sign_count=registration.sign_count,
            transports=transports,
        )

        self.redis.store(
            key=new_credential.id,
            value=json.dumps(new_credential.dict()),
            expiration_seconds=60 * 60 * 24,  # 24 hours
        )

        return new_credential

    def retrieve_credential_by_id(self, *, credential_id: str) -> WebAuthnCredential:
        """
        Retrieve a credential from Redis

        Raises `homepage.exceptions.InvalidCredentialID` if the given credential ID is invalid
        """
        pass

    def retrieve_credentials_by_username(self, *, username: str) -> List[WebAuthnCredential]:
        return []

    def update_credential_sign_count(self, *, credential_id: str, new_sign_count: int) -> None:
        """
        Update a credential's number of times it's been used

        Raises `homepage.exceptions.InvalidCredentialID` if the given credential ID is invalid
        """
        pass
