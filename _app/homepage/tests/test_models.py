import json
from django.test import TestCase

from homepage.models import WebAuthnCredential
from webauthn.helpers.structs import AuthenticatorTransport, CredentialDeviceType

CRED_ID = "m-nPE6tAs2f1eAz2Gd6b9A"
CRED_PUBLIC_KEY = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEV1xF0vpUlLsCsuw9Vawaaew9UrgxGTjaRx-y98kKNMMMqNFZJjUzF3xWP6Jqt-n4QWIC_VaPBnvq_zwkc-T0GA"


class TestWebAuthnCredential(TestCase):
    def setUp(self):
        self.default_cred_dict = {
            "id": CRED_ID,
            "public_key": CRED_PUBLIC_KEY,
            "username": "mmiller",
            "sign_count": 0,
            "is_discoverable_credential": True,
            "device_type": CredentialDeviceType.MULTI_DEVICE.value,
            "backed_up": True,
            "transports": ["internal", "hybrid"],
            "aaguid": "00000000-0000-0000-0000-000000000000",
        }

        self.default_cred_model = WebAuthnCredential(
            id=CRED_ID,
            public_key=CRED_PUBLIC_KEY,
            username="mmiller",
            sign_count=0,
            is_discoverable_credential=True,
            device_type=CredentialDeviceType.MULTI_DEVICE,
            backed_up=True,
            transports=[AuthenticatorTransport.INTERNAL, AuthenticatorTransport.HYBRID],
            aaguid="00000000-0000-0000-0000-000000000000",
        )

    def test_from_json_str(self):
        cred = WebAuthnCredential.from_json(json.dumps(self.default_cred_dict))

        self.assertEqual(cred.id, CRED_ID)
        self.assertEqual(cred.public_key, CRED_PUBLIC_KEY)
        self.assertEqual(cred.username, "mmiller")
        self.assertEqual(cred.sign_count, 0)
        self.assertEqual(cred.is_discoverable_credential, True)
        self.assertEqual(cred.device_type, CredentialDeviceType.MULTI_DEVICE)
        self.assertEqual(cred.backed_up, True)
        self.assertEqual(
            cred.transports, [AuthenticatorTransport.INTERNAL, AuthenticatorTransport.HYBRID]
        )
        self.assertEqual(cred.aaguid, "00000000-0000-0000-0000-000000000000")

    def test_from_json_dict(self):
        cred = WebAuthnCredential.from_json(self.default_cred_dict)

        self.assertEqual(cred.id, CRED_ID)
        self.assertEqual(cred.public_key, CRED_PUBLIC_KEY)
        self.assertEqual(cred.username, "mmiller")
        self.assertEqual(cred.sign_count, 0)
        self.assertEqual(cred.is_discoverable_credential, True)
        self.assertEqual(cred.device_type, CredentialDeviceType.MULTI_DEVICE)
        self.assertEqual(cred.backed_up, True)
        self.assertEqual(
            cred.transports, [AuthenticatorTransport.INTERNAL, AuthenticatorTransport.HYBRID]
        )
        self.assertEqual(cred.aaguid, "00000000-0000-0000-0000-000000000000")

    def test_from_json_no_transports(self):
        self.default_cred_dict["transports"] = None
        cred = WebAuthnCredential.from_json(self.default_cred_dict)

        self.assertIsNone(cred.transports)

    def test_from_json_unknown_discoverability(self):
        self.default_cred_dict["is_discoverable_credential"] = None
        cred = WebAuthnCredential.from_json(self.default_cred_dict)

        self.assertIsNone(cred.is_discoverable_credential)

    def test_to_json(self):
        cred_json = self.default_cred_model.to_json()

        self.assertEqual(cred_json["id"], CRED_ID)
        self.assertEqual(cred_json["public_key"], CRED_PUBLIC_KEY)
        self.assertEqual(cred_json["username"], "mmiller")
        self.assertEqual(cred_json["sign_count"], 0)
        self.assertEqual(cred_json["is_discoverable_credential"], True)
        self.assertEqual(cred_json["device_type"], "multi_device")
        self.assertEqual(cred_json["backed_up"], True)
        self.assertEqual(cred_json["transports"], ["internal", "hybrid"])
        self.assertEqual(cred_json["aaguid"], "00000000-0000-0000-0000-000000000000")

    def test_to_json_no_transports(self):
        self.default_cred_model.transports = None
        cred_json = self.default_cred_model.to_json()

        self.assertIsNone(cred_json["transports"])

    def test_to_json_unknown_discoverability(self):
        self.default_cred_model.is_discoverable_credential = None
        cred_json = self.default_cred_model.to_json()

        self.assertIsNone(cred_json["is_discoverable_credential"])
