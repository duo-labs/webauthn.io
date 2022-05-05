import json

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from webauthn.helpers.structs import (
    RegistrationCredential,
)

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
    username = form_data["username"]
    response = form_data["response"]

    registration_service = RegistrationService()

    try:
        credential = RegistrationCredential.parse_raw(json.dumps(response))
        registration_service.verify_registration_response(username=username, credential=credential)
    except Exception as err:
        return JsonResponseBadRequest(err, safe=False)

    return JsonResponse({"verified": True})
