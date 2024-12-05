from unittest.mock import MagicMock
from django.conf import settings
from django.test import TestCase
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from webauthn.helpers.structs import (
    PublicKeyCredentialParameters,
    PublicKeyCredentialHint,
    AttestationConveyancePreference,
    AuthenticatorAttachment,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from homepage.services import RegistrationService


class TestRegistrationService(TestCase):
    def setUp(self):
        settings.RP_ID = "webauthn.io"
        settings.RP_NAME = "webauthn.io (name)"
        self.service = RegistrationService(redis=MagicMock())

    def test_generate_options(self):
        options = self.service.generate_registration_options(
            username="mmiller",
            algorithms=["ed25519", "es256"],
            attachment="platform",
            attestation="direct",
            discoverable_credential="required",
            existing_credentials=[],
            hints=[],
            user_verification="discouraged",
        )

        # Get mypy to chill out about optionality of `authenticator_selection`
        assert options.authenticator_selection

        self.assertEqual(options.rp.id, "webauthn.io")
        self.assertEqual(options.rp.name, "webauthn.io (name)")
        self.assertEqual(options.user.name, "mmiller")
        self.assertEqual(options.attestation, AttestationConveyancePreference.DIRECT)
        self.assertEqual(
            options.authenticator_selection.authenticator_attachment,
            AuthenticatorAttachment.PLATFORM,
        )
        self.assertEqual(
            options.authenticator_selection.resident_key,
            ResidentKeyRequirement.REQUIRED,
        )
        self.assertEqual(
            options.authenticator_selection.require_resident_key,
            True,
        )
        self.assertEqual(
            options.authenticator_selection.user_verification,
            UserVerificationRequirement.DISCOURAGED,
        )

    def test_options_pub_key_alg_ed25519_is_first(self):
        options = self.service.generate_registration_options(
            username="mmiller",
            algorithms=["ed25519", "es256"],
            attachment="",
            attestation="",
            discoverable_credential="",
            existing_credentials=[],
            hints=[],
            user_verification="",
        )

        self.assertEqual(len(options.pub_key_cred_params), 2)
        self.assertEqual(
            options.pub_key_cred_params[0],
            PublicKeyCredentialParameters(alg=COSEAlgorithmIdentifier.EDDSA, type="public-key"),
        )

    def test_parse_hints(self) -> None:
        options = self.service.generate_registration_options(
            username="mmiller",
            algorithms=["ed25519", "es256"],
            attachment="all",
            attestation="direct",
            discoverable_credential="required",
            existing_credentials=[],
            user_verification="discouraged",
            hints=["client-device", "security-key", "hybrid"],
        )

        self.assertEqual(
            options.hints,
            [
                PublicKeyCredentialHint.CLIENT_DEVICE,
                PublicKeyCredentialHint.SECURITY_KEY,
                PublicKeyCredentialHint.HYBRID,
            ],
        )

    def test_hints_do_not_change_attachment(self) -> None:
        options = self.service.generate_registration_options(
            username="mmiller",
            algorithms=["ed25519", "es256"],
            attestation="direct",
            discoverable_credential="required",
            existing_credentials=[],
            user_verification="discouraged",
            # Sometimes it's useful to test conflicting options like this to gauge browser behavior
            attachment="platform",
            hints=["security-key", "hybrid"],
        )

        assert options.authenticator_selection

        self.assertEqual(
            options.authenticator_selection.authenticator_attachment,
            AuthenticatorAttachment.PLATFORM,
        )
        self.assertEqual(
            options.hints,
            [PublicKeyCredentialHint.SECURITY_KEY, PublicKeyCredentialHint.HYBRID],
        )
