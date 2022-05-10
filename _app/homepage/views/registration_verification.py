import json

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from homepage.services.credential import CredentialService

from homepage.services.registration import RegistrationService
from homepage.forms import RegistrationResponseForm
from homepage.response import JsonResponseBadRequest


@csrf_exempt
def registration_verification(request: HttpRequest) -> JsonResponse:
    """
    Verify the response from a WebAuthn registration ceremony
    """

    body_json: dict = json.loads(request.body)

    response_form = RegistrationResponseForm(body_json)

    if not response_form.is_valid():
        return JsonResponseBadRequest(dict(response_form.errors.items()))

    form_data = response_form.cleaned_data
    username: str = form_data["username"]
    webauthn_response: dict = form_data["response"]

    registration_service = RegistrationService()

    try:
        verification = registration_service.verify_registration_response(
            username=username,
            response=webauthn_response,
        )

        transports: list = webauthn_response.get("transports", [])
        extensions: dict = webauthn_response.get("clientExtensionResults", {})
        ext_cred_props: dict = extensions.get("credProps", {})
        is_discoverable_credential: bool = ext_cred_props.get("rk", False)

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
