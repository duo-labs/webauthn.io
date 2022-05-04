import json
from typing import List, Optional

from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from webauthn import generate_registration_options, options_to_json
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    AuthenticatorAttachment,
    UserVerificationRequirement,
    COSEAlgorithmIdentifier,
)

from .forms import UsernameForm, RegistrationOptionsRequestForm
from .const import libraries


def index(request):
    """
    Render the homepage
    """
    username_form = UsernameForm()
    context = {
        "username_form": username_form,
        "libraries": libraries,
    }

    return render(request, "homepage/index.html", context)


def profile(request):
    """
    Render the logged-in user's "profile" page
    """
    context = {
        "libraries": libraries,
    }

    return render(request, "homepage/profile.html", context)


@csrf_exempt
def registration_options(request: HttpRequest):
    body_json: dict = json.loads(request.body)
    options_form = RegistrationOptionsRequestForm(body_json)

    if not options_form.is_valid():
        resp = JsonResponse(dict(options_form.errors.items()))
        resp.status_code = 400
        return resp

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
        rp_id="webauthn.io",
        rp_name="WebAuthn.io",
        user_id=options_username,
        user_name=options_username,
        attestation=attestation,
        authenticator_selection=authenticator_selection,
        supported_pub_key_algs=supported_pub_key_algs,
    )
    return JsonResponse(json.loads(options_to_json(registration_options)))
