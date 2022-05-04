import json
from typing import List, Optional

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from webauthn import generate_registration_options, options_to_json
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    AuthenticatorAttachment,
    UserVerificationRequirement,
    COSEAlgorithmIdentifier,
)

from homepage.services import RegistrationService
from homepage.forms import RegistrationOptionsRequestForm
from homepage.response import JsonResponseBadRequest


@csrf_exempt
def registration_options(request: HttpRequest) -> JsonResponse:
    """
    Generate options for a WebAuthn registration ceremony
    """

    body_json: dict = json.loads(request.body)

    # TODO: Move this all into RegistrationService?
    options_form = RegistrationOptionsRequestForm(body_json)

    if not options_form.is_valid():
        return JsonResponseBadRequest(dict(options_form.errors.items()))

    form_data = options_form.cleaned_data
    options_attestation = form_data["attestation"]
    options_attachment = form_data["attachment"]
    options_require_user_verification = form_data["require_user_verification"]
    options_algorithms = form_data["algorithms"]
    options_username = form_data["username"]

    attestation = AttestationConveyancePreference.NONE
    if options_attestation == "direct":
        attestation = AttestationConveyancePreference.DIRECT

    authenticator_selection = AuthenticatorSelectionCriteria(
        user_verification=UserVerificationRequirement.DISCOURAGED,
    )
    if options_attachment != "all":
        attachment = AuthenticatorAttachment.CROSS_PLATFORM
        if options_attachment == "platform":
            attachment = AuthenticatorAttachment.PLATFORM

        authenticator_selection.authenticator_attachment = attachment

    if options_require_user_verification:
        authenticator_selection.user_verification = UserVerificationRequirement.REQUIRED

    supported_pub_key_algs: Optional[List[COSEAlgorithmIdentifier]] = None
    if len(options_algorithms) > 0:
        supported_pub_key_algs = []

        if "es256" in options_algorithms:
            supported_pub_key_algs.append(COSEAlgorithmIdentifier.ECDSA_SHA_256)

        if "rs256" in options_algorithms:
            supported_pub_key_algs.append(COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256)

    registration_options = generate_registration_options(
        rp_id=settings.RP_ID,
        rp_name=settings.RP_NAME,
        user_id=options_username,
        user_name=options_username,
        attestation=attestation,
        authenticator_selection=authenticator_selection,
        supported_pub_key_algs=supported_pub_key_algs,
    )

    registration_service = RegistrationService()
    registration_service.save_options(username=options_username, options=registration_options)

    return JsonResponse(json.loads(options_to_json(registration_options)))
