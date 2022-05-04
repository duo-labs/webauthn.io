from typing import Union

from django.conf import settings
from webauthn import options_to_json, verify_registration_response
from webauthn.helpers.structs import (
    PublicKeyCredentialCreationOptions,
    RegistrationCredential,
    UserVerificationRequirement,
)
from webauthn.helpers import json_loads_base64url_to_bytes, base64url_to_bytes

from homepage.services import RedisService
from homepage.exceptions import InvalidRegistrationSession


class RegistrationService:
    redis: RedisService

    def __init__(self):
        self.redis = RedisService(db=2)

    def verify_registration_response(self, *, username: str, credential: RegistrationCredential):
        options = self._get_options(username=username)

        if not options:
            raise InvalidRegistrationSession(f"no options for user {username}")

        require_user_verification = False
        if options.authenticator_selection:
            require_user_verification = (
                options.authenticator_selection.user_verification
                == UserVerificationRequirement.REQUIRED
            )

        self._delete_options(username=username)

        return verify_registration_response(
            credential=credential,
            expected_challenge=options.challenge,
            expected_rp_id=settings.RP_ID,
            expected_origin=settings.RP_EXPECTED_ORIGIN,
            require_user_verification=require_user_verification,
        )

    def save_options(self, username: str, options: PublicKeyCredentialCreationOptions):
        """
        Store registration options for the user so we can reference them later
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

    def _get_options(self, username: str) -> Union[PublicKeyCredentialCreationOptions, None]:
        """
        Attempt to retrieve saved registration options for the user
        """
        options: str = self.redis.retrieve(key=username)
        if options is None:
            return options

        # We can't use PublicKeyCredentialCreationOptions.parse_raw() because
        # json_loads_base64url_to_bytes() doesn't know to convert these few values to bytes, so we
        # have to do it manually
        options_json: dict = json_loads_base64url_to_bytes(options)
        options_json["user"]["id"] = base64url_to_bytes(options_json["user"]["id"])
        options_json["challenge"] = base64url_to_bytes(options_json["challenge"])

        return PublicKeyCredentialCreationOptions.parse_obj(options_json)

    def _delete_options(self, username: str) -> int:
        return self.redis.delete(key=username)
