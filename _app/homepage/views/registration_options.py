import json

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from webauthn import options_to_json

from homepage.services import RegistrationService, CredentialService
from homepage.forms import RegistrationOptionsRequestForm
from homepage.response import JsonResponseBadRequest


@csrf_exempt
def registration_options(request: HttpRequest) -> JsonResponse:
    """
    Generate options for a WebAuthn registration ceremony
    """

    body_json: dict = json.loads(request.body)

    options_form = RegistrationOptionsRequestForm(body_json)

    if not options_form.is_valid():
        return JsonResponseBadRequest(dict(options_form.errors.items()))

    form_data = options_form.cleaned_data
    options_attestation = form_data["attestation"]
    options_attachment = form_data["attachment"]
    options_user_verification = form_data["user_verification"]
    options_algorithms = form_data["algorithms"]
    options_username = form_data["username"]
    options_discoverable_credential = form_data["discoverable_credential"]
    options_hints = form_data["hints"]

    registration_service = RegistrationService()
    credential_service = CredentialService()

    registration_options = registration_service.generate_registration_options(
        username=options_username,
        attachment=options_attachment,
        attestation=options_attestation,
        algorithms=options_algorithms,
        user_verification=options_user_verification,
        existing_credentials=credential_service.retrieve_credentials_by_username(
            username=options_username
        ),
        discoverable_credential=options_discoverable_credential,
        hints=options_hints,
    )

    options_json = json.loads(options_to_json(registration_options))

    # Tack on hints (till py_webauthn learns about hints and we can handle it in the service)
    options_json["hints"] = options_hints

    # Add in credProps extension
    options_json["extensions"] = {
        "credProps": True,
    }

    return JsonResponse(options_json)
