import json

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from webauthn.helpers.structs import ResidentKeyRequirement

from homepage.services.credential import CredentialService
from homepage.services.registration import RegistrationService
from homepage.forms import RegistrationResponseForm
from homepage.response import JsonResponseBadRequest


@csrf_exempt
def registration_verification(request: HttpRequest) -> JsonResponse:
    """
    Verify the response from a WebAuthn registration ceremony
    """

    try:
        body_json: dict = json.loads(request.body)
    except Exception as exc:
        return JsonResponseBadRequest({"error": f"Could not parse options: {str(exc)}"})

    response_form = RegistrationResponseForm(body_json)

    if not response_form.is_valid():
        return JsonResponseBadRequest(dict(response_form.errors.items()))

    form_data = response_form.cleaned_data
    username: str = form_data["username"]
    webauthn_response: dict = form_data["response"]

    registration_service = RegistrationService()

    try:
        (verification, options) = registration_service.verify_registration_response(
            username=username,
            response=webauthn_response,
        )

        _response: dict = webauthn_response.get("response", {})
        transports: list = _response.get("transports", [])

        # Try to determine if the credential we got is a discoverable credential
        is_discoverable_credential = None

        # If credProps.rk is defined then use that as the most definitive signal
        extensions: dict = webauthn_response.get("clientExtensionResults", {})
        ext_cred_props: dict | None = extensions.get("credProps", None)
        if ext_cred_props is not None:
            ext_cred_props_rk: bool | None = ext_cred_props.get("rk", None)
            if ext_cred_props_rk is not None:
                is_discoverable_credential = bool(ext_cred_props_rk)

        # If we can't determine this using credProps then let's look at the registration options
        if is_discoverable_credential is None:
            if options.authenticator_selection.resident_key == ResidentKeyRequirement.REQUIRED:
                is_discoverable_credential = True

        # Store credential for later
        credential_service = CredentialService()
        credential_service.store_credential(
            username=username,
            verification=verification,
            transports=transports,
            is_discoverable_credential=is_discoverable_credential,
        )
    except Exception as err:
        return JsonResponseBadRequest({"error": str(err)})

    return JsonResponse({"verified": True})
