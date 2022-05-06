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
        registration = registration_service.verify_registration_response(
            username=username, response=webauthn_response
        )

        credential_service = CredentialService()

        transports = []
        if "transports" in webauthn_response:
            transports = webauthn_response["transports"]

        credential_service.store_credential(
            username=username, registration=registration, transports=transports
        )
    except Exception as err:
        return JsonResponseBadRequest(err, safe=False)

    return JsonResponse({"verified": True})
