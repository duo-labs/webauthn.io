import json

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from webauthn import options_to_json

from homepage.services import AuthenticationService, CredentialService
from homepage.forms import AuthenticationOptionsRequestForm
from homepage.response import JsonResponseBadRequest


@csrf_exempt
def authentication_options(request: HttpRequest) -> JsonResponse:
    body_json: dict = json.loads(request.body)

    options_form = AuthenticationOptionsRequestForm(body_json)

    if not options_form.is_valid():
        return JsonResponseBadRequest(dict(options_form.errors.items()))

    form_data = options_form.cleaned_data
    options_username = form_data["username"]
    options_require_user_verification = form_data["require_user_verification"]
    options_only_registered_authenticators = form_data["only_registered_authenticators"]

    authentication_service = AuthenticationService()

    existing_credentials = []
    if options_only_registered_authenticators:
        credential_service = CredentialService()
        existing_credentials = credential_service.retrieve_credentials_by_username(
            username=options_username
        )

    authentication_options = authentication_service.generate_authentication_options(
        username=options_username,
        require_user_verification=options_require_user_verification,
        existing_credentials=existing_credentials,
    )

    return JsonResponse(json.loads(options_to_json(authentication_options)))
