from django.test import TestCase
from django.urls import reverse
from webauthn.helpers import base64url_to_bytes
from webauthn.registration.verify_registration_response import VerifiedRegistration
from webauthn.helpers.structs import (
    CredentialDeviceType,
    AttestationFormat,
    PublicKeyCredentialType,
)

from homepage.services import SessionService, CredentialService

credential_id = "AAAA"
registered_passkey = VerifiedRegistration(
    credential_id=base64url_to_bytes(credential_id),
    credential_public_key=base64url_to_bytes(
        "pQECAyYgASFYIEhW1CRfuNlIN6XTPKw0RbvzeaIlRMrDwwep-uq_-3WQIlgg1FZwd_RZRsqS_qgKCDvcVh7ScoKNo3w5h5fv3ihUSww"
    ),
    aaguid="00000000-0000-0000-0000-00000000",
    attestation_object=base64url_to_bytes(
        "o2NmbXRkbm9uZWdhdHRTdG10oGhhdXRoRGF0YVjESZYN5YgOjGh0NBcPZHZgW4_krrmihjLHmVzzuoMdl2NFAAAAFwAAAAAAAAAAAAAAAAAAAAAAQPctcQPE5oNRRJk_nO_371mf7qE7qIodzr0eOf6ACvnMB1oQG165dqutoi1U44shGezu5_gkTjmOPeJO0N8a7P-lAQIDJiABIVggSFbUJF-42Ug3pdM8rDRFu_N5oiVEysPDB6n66r_7dZAiWCDUVnB39FlGypL-qAoIO9xWHtJygo2jfDmHl-_eKFRLDA"
    ),
    credential_backed_up=True,
    credential_device_type=CredentialDeviceType.MULTI_DEVICE,
    credential_type=PublicKeyCredentialType.PUBLIC_KEY,
    fmt=AttestationFormat.NONE,
    sign_count=0,
    user_verified=True,
)


class TestViewProfile(TestCase):
    route = reverse("profile")
    credential_service = CredentialService()
    session_service = SessionService()
    username = "mmiller"

    def setUp(self):
        # The user has authenticated
        self.client.get(reverse("index"))
        self.session_service.log_in_user(session=self.client.session, username=self.username)

    def tearDown(self) -> None:
        self.client.cookies.clear()

    def test_sets_debug_cookie_with_query_param(self) -> None:
        # The user set the magic query parameter to get the "debug" cookie
        self.client.get(self.route, QUERY_STRING="debug=true")

        cookie_debug = self.client.cookies.get("debug")
        self.assertIsNotNone(cookie_debug)
        assert cookie_debug  # for mypy
        self.assertEqual(str(cookie_debug.coded_value), "true")

    def test_no_debug_hide_pubkey_kty_and_alg(self) -> None:
        # Pretend the user's registered the following passkey
        self.credential_service.store_credential(
            username=self.username,
            verification=registered_passkey,
        )

        # The user wants to see debug info
        response = self.client.get(self.route)

        html_doc = str(response.content)

        self.assertEqual(html_doc.find("Public Key Type"), -1)
        self.assertEqual(html_doc.find("(EC2)"), -1)
        self.assertEqual(html_doc.find("Public Key Algorithm"), -1)
        self.assertEqual(html_doc.find("ECDSA-SHA-256 (-7)"), -1)

        self.credential_service.delete_credential_by_id(credential_id=credential_id)

    def test_debug_show_pubkey_kty_and_alg(self) -> None:
        # Pretend the user's registered the following passkey
        self.credential_service.store_credential(
            username=self.username,
            verification=registered_passkey,
        )

        # The user wants to see debug info
        response = self.client.get(self.route, QUERY_STRING="debug=true")

        html_doc = str(response.content)

        self.assertGreater(html_doc.find("Public Key Type"), -1)
        self.assertGreater(html_doc.find("EC2 (2)"), -1)
        self.assertGreater(html_doc.find("Public Key Algorithm"), -1)
        self.assertGreater(html_doc.find("ECDSA-SHA-256 (-7)"), -1)

        self.credential_service.delete_credential_by_id(credential_id=credential_id)
