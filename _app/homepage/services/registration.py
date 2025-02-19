from typing import Union, List, Optional
import secrets

from django.conf import settings
from webauthn import (
    generate_registration_options,
    options_to_json,
    verify_registration_response,
)
from webauthn.helpers import (
    base64url_to_bytes,
    parse_registration_credential_json,
    parse_registration_options_json,
)
from webauthn.helpers.structs import (
    PublicKeyCredentialCreationOptions,
    UserVerificationRequirement,
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    AuthenticatorAttachment,
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialHint,
    ResidentKeyRequirement,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier

from homepage.services import RedisService
from homepage.exceptions import InvalidRegistrationSession
from homepage.models import WebAuthnCredential


class RegistrationService:
    redis: RedisService

    def __init__(self, redis=RedisService(db=2)):
        self.redis = redis

    def generate_registration_options(
        self,
        *,
        username: str,
        attestation: str,
        attachment: str,
        user_verification: str,
        algorithms: List[str],
        existing_credentials: List[WebAuthnCredential],
        discoverable_credential: str,
        hints: List[str],
    ):
        _attestation = AttestationConveyancePreference.NONE

        if attestation == "direct":
            _attestation = AttestationConveyancePreference.DIRECT

        authenticator_selection = AuthenticatorSelectionCriteria(
            user_verification=UserVerificationRequirement.DISCOURAGED,
            resident_key=ResidentKeyRequirement.PREFERRED,
        )
        if attachment != "all":
            authenticator_attachment = AuthenticatorAttachment.CROSS_PLATFORM
            if attachment == "platform":
                authenticator_attachment = AuthenticatorAttachment.PLATFORM

            authenticator_selection.authenticator_attachment = authenticator_attachment

        if user_verification == "discouraged":
            authenticator_selection.user_verification = UserVerificationRequirement.DISCOURAGED
        elif user_verification == "preferred":
            authenticator_selection.user_verification = UserVerificationRequirement.PREFERRED
        elif user_verification == "required":
            authenticator_selection.user_verification = UserVerificationRequirement.REQUIRED

        if discoverable_credential == "discouraged":
            authenticator_selection.resident_key = ResidentKeyRequirement.DISCOURAGED
        elif discoverable_credential == "preferred":
            authenticator_selection.resident_key = ResidentKeyRequirement.PREFERRED
        elif discoverable_credential == "required":
            authenticator_selection.resident_key = ResidentKeyRequirement.REQUIRED

        supported_pub_key_algs: Optional[List[COSEAlgorithmIdentifier]] = None
        if len(algorithms) > 0:
            supported_pub_key_algs = []

            if "ed25519" in algorithms:
                supported_pub_key_algs.append(COSEAlgorithmIdentifier.EDDSA)

            if "es256" in algorithms:
                supported_pub_key_algs.append(COSEAlgorithmIdentifier.ECDSA_SHA_256)

            if "rs256" in algorithms:
                supported_pub_key_algs.append(COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256)

        _hints = [PublicKeyCredentialHint(hint) for hint in hints]

        registration_options = generate_registration_options(
            rp_id=settings.RP_ID,
            rp_name=settings.RP_NAME,
            user_name=username,
            user_id=f"webauthnio-{username}".encode(),
            attestation=_attestation,
            authenticator_selection=authenticator_selection,
            supported_pub_key_algs=supported_pub_key_algs,
            exclude_credentials=[
                PublicKeyCredentialDescriptor(
                    id=base64url_to_bytes(cred.id), transports=cred.transports
                )
                for cred in existing_credentials
            ],
            hints=_hints,
        )

        # py_webauthn will default to all supported algorithms on an empty `algorithms` list
        # so clear it manually so we can test out that scenario
        if len(algorithms) == 0:
            registration_options.pub_key_cred_params = []

        self._save_options(username=username, options=registration_options)

        return registration_options

    def verify_registration_response(self, *, username: str, response: dict):
        credential = parse_registration_credential_json(response)
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

        verification = verify_registration_response(
            credential=credential,
            expected_challenge=options.challenge,
            expected_rp_id=settings.RP_ID,
            expected_origin=settings.RP_EXPECTED_ORIGIN,
            require_user_verification=require_user_verification,
        )

        return (
            verification,
            options,
        )

    def _save_options(self, username: str, options: PublicKeyCredentialCreationOptions):
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
        options: str | None = self.redis.retrieve(key=username)
        if options is None:
            return options

        return parse_registration_options_json(options)

    def _delete_options(self, username: str) -> int:
        return self.redis.delete(key=username)
