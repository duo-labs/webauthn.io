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

    def test_options_pub_key_cred_params_order(self):
        options = self.service.generate_registration_options(
            username="mmiller",
            # Purposefully putting algs in reverse order, from least to most desirable
            algorithms=["rs256", "es256", "ed25519", "mldsa87", "mldsa65", "mldsa44"],
            attachment="",
            attestation="",
            discoverable_credential="",
            existing_credentials=[],
            hints=[],
            user_verification="",
        )

        pk_cred_params = options.pub_key_cred_params

        self.assertEqual(len(options.pub_key_cred_params), 6)
        self.assertEqual(pk_cred_params[0].alg, COSEAlgorithmIdentifier.ML_DSA_44)
        self.assertEqual(pk_cred_params[1].alg, COSEAlgorithmIdentifier.ML_DSA_65)
        self.assertEqual(pk_cred_params[2].alg, COSEAlgorithmIdentifier.ML_DSA_87)
        self.assertEqual(pk_cred_params[3].alg, COSEAlgorithmIdentifier.EDDSA)
        self.assertEqual(pk_cred_params[4].alg, COSEAlgorithmIdentifier.ECDSA_SHA_256)
        self.assertEqual(pk_cred_params[5].alg, COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256)

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

    def test_set_attachment_platform(self) -> None:
        options = self.service.generate_registration_options(
            username="mmiller",
            algorithms=["ed25519", "es256"],
            attestation="direct",
            discoverable_credential="required",
            existing_credentials=[],
            user_verification="discouraged",
            hints=["client-device", "security-key", "hybrid"],
            # Support security keys and hybrid
            attachment="cross-platform",
        )

        assert options.authenticator_selection

        self.assertEqual(
            options.authenticator_selection.authenticator_attachment,
            AuthenticatorAttachment.CROSS_PLATFORM,
        )

    def test_set_attachment_cross_platform(self) -> None:
        options = self.service.generate_registration_options(
            username="mmiller",
            algorithms=["ed25519", "es256"],
            attestation="direct",
            discoverable_credential="required",
            existing_credentials=[],
            user_verification="discouraged",
            hints=["client-device", "security-key", "hybrid"],
            # Support only platform authenticators
            attachment="platform",
        )

        assert options.authenticator_selection

        self.assertEqual(
            options.authenticator_selection.authenticator_attachment,
            AuthenticatorAttachment.PLATFORM,
        )

    def test_set_attachment_all(self) -> None:
        options = self.service.generate_registration_options(
            username="mmiller",
            algorithms=["ed25519", "es256"],
            attestation="direct",
            discoverable_credential="required",
            existing_credentials=[],
            user_verification="discouraged",
            hints=[],
            # Support everything
            attachment="all",
        )

        assert options.authenticator_selection

        self.assertIsNone(options.authenticator_selection.authenticator_attachment)

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
