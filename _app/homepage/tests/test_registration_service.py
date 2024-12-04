from unittest.mock import MagicMock
from django.conf import settings
from django.test import TestCase
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from webauthn.helpers.structs import (
    PublicKeyCredentialParameters,
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

