from typing import List, Union

from django.conf import settings
from webauthn import generate_authentication_options, options_to_json
from webauthn.helpers import json_loads_base64url_to_bytes, base64url_to_bytes
from webauthn.helpers.structs import (
    PublicKeyCredentialRequestOptions,
    UserVerificationRequirement,
    PublicKeyCredentialDescriptor,
)

from homepage.services import RedisService
from homepage.models import WebAuthnCredential


class AuthenticationService:
    redis: RedisService

    def __init__(self):
        self.redis = RedisService(db=3)

    def generate_authentication_options(
        self,
        *,
        username: str,
        require_user_verification: bool,
        existing_credentials: List[WebAuthnCredential],
    ) -> PublicKeyCredentialRequestOptions:
        """
        Generate and store authentication options
        """

        user_verification = UserVerificationRequirement.DISCOURAGED
        if require_user_verification:
            user_verification = UserVerificationRequirement.REQUIRED

        authentication_options = generate_authentication_options(
            rp_id=settings.RP_ID,
            user_verification=user_verification,
            allow_credentials=[
                PublicKeyCredentialDescriptor(
                    id=base64url_to_bytes(cred.id), transports=cred.transports
                )
                for cred in existing_credentials
            ],
        )

        self._save_options(username=username, options=authentication_options)

        return authentication_options

    def _save_options(self, *, username: str, options: PublicKeyCredentialRequestOptions):
        """
        Store authentication options for the user so we can reference them later
        """
        expiration = options.timeout
        if type(expiration) is int:
            # Store them temporarily, for twice as long as we're telling WebAuthn how long it
            # should give the user to complete the WebAuthn ceremony
            expiration = int(expiration / 1000 * 2)
        else:
            # Default to two minutes since we default timeout to 60 seconds
            expiration = 120

        return self.redis.store(
            key=username, value=options_to_json(options), expiration_seconds=expiration
        )

    def _get_options(self, *, username: str) -> Union[PublicKeyCredentialRequestOptions, None]:
        """
        Attempt to retrieve saved authentication options for the user
        """
        options: str = self.redis.retrieve(key=username)
        if options is None:
            return options

        # We can't use PublicKeyCredentialRequestOptions.parse_raw() because
        # json_loads_base64url_to_bytes() doesn't know to convert these few values to bytes, so we
        # have to do it manually
        options_json: dict = json_loads_base64url_to_bytes(options)
        options_json["challenge"] = base64url_to_bytes(options_json["challenge"])
        options_json["allowCredentials"] = [
            {**cred, "id": base64url_to_bytes(cred["id"])}
            for cred in options_json["excludeCredentials"]
        ]

        return PublicKeyCredentialRequestOptions.parse_obj(options_json)

    def _delete_options(self, *, username: str) -> int:
        return self.redis.delete(key=username)
