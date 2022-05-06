from typing import List, Union
import json

from django.conf import settings
from webauthn import (
    generate_authentication_options,
    options_to_json,
    verify_authentication_response,
)
from webauthn.helpers import json_loads_base64url_to_bytes, base64url_to_bytes
from webauthn.helpers.structs import (
    PublicKeyCredentialRequestOptions,
    UserVerificationRequirement,
    PublicKeyCredentialDescriptor,
    AuthenticationCredential,
)

from homepage.services import RedisService
from homepage.models import WebAuthnCredential
from homepage.exceptions import InvalidAuthenticationResponse


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

    def verify_authentication_response(
        self,
        *,
        username: str,
        existing_credential: WebAuthnCredential,
        response: dict,
    ):
        credential = AuthenticationCredential.parse_raw(json.dumps(response))
        options = self._get_options(username=username)

        if not options:
            raise InvalidAuthenticationResponse(f"no options for user {username}")

        require_user_verification = False
        if options.user_verification:
            require_user_verification = (
                options.user_verification == UserVerificationRequirement.REQUIRED
            )

        self._delete_options(username=username)

        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=options.challenge,
            expected_rp_id=settings.RP_ID,
            expected_origin=settings.RP_EXPECTED_ORIGIN,
            require_user_verification=require_user_verification,
            credential_public_key=base64url_to_bytes(existing_credential.public_key),
            credential_current_sign_count=existing_credential.sign_count,
        )

        return verification

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
