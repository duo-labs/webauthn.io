from typing import List, Optional
import json

from webauthn.registration.verify_registration_response import VerifiedRegistration
from webauthn.authentication.verify_authentication_response import VerifiedAuthentication
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
        verification: VerifiedRegistration,
        transports: Optional[List[str]] = None,
    ) -> WebAuthnCredential:
        """
        Temporarily store a new credential in Redis so we can leverage its record expiration to
        remove credentials after a certain number of hours

        The Redis key will be the base64url-encoded credential ID
        """
        new_credential = WebAuthnCredential(
            username=username,
            id=bytes_to_base64url(verification.credential_id),
            public_key=bytes_to_base64url(verification.credential_public_key),
            sign_count=verification.sign_count,
            transports=transports,
        )

        self._temporarily_store_in_redis(new_credential)

        return new_credential

    def retrieve_credential_by_id(
        self,
        *,
        credential_id: str,
        username: Optional[str] = None,
    ) -> WebAuthnCredential:
        """
        Retrieve a credential from Redis

        Raises `homepage.exceptions.InvalidCredentialID` if the given credential ID is invalid
        """
        raw_credential: str | None = self.redis.retrieve(key=credential_id)

        if not raw_credential:
            raise InvalidCredentialID("Credential does not exist")

        credential = WebAuthnCredential.parse_raw(raw_credential)

        if username and credential.username != username:
            raise InvalidCredentialID("Credential does not belong to user")

        return credential

    def retrieve_credentials_by_username(self, *, username: str) -> List[WebAuthnCredential]:
        """
        Get all credentials for a given user
        """
        credentials = [WebAuthnCredential.parse_raw(cred) for cred in self.redis.retrieve_all()]

        return [cred for cred in credentials if cred.username == username]

    def update_credential_sign_count(self, *, verification: VerifiedAuthentication) -> None:
        """
        Update a credential's number of times it's been used

        Raises `homepage.exceptions.InvalidCredentialID` if the given credential ID is invalid
        """
        credential_id = bytes_to_base64url(verification.credential_id)
        raw_credential: str | None = self.redis.retrieve(key=credential_id)

        if not raw_credential:
            raise InvalidCredentialID()

        credential = WebAuthnCredential.parse_raw(raw_credential)

        credential.sign_count = verification.new_sign_count

        self._temporarily_store_in_redis(credential)

    def _temporarily_store_in_redis(self, credential: WebAuthnCredential) -> None:
        """
        We only ever want to save credentials for a finite period of time
        """
        self.redis.store(
            key=credential.id,
            value=json.dumps(credential.dict()),
            expiration_seconds=60 * 60 * 24,  # 24 hours
        )
