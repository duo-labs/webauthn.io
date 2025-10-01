import json

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt

from homepage.services import AuthenticationService, CredentialService, SessionService
from homepage.forms import AuthenticationResponseForm
from homepage.response import JsonResponseBadRequest


@csrf_exempt
def authentication_verification(request: HttpRequest) -> JsonResponse:
    """
    Verify the response from a WebAuthn authentication ceremony
    """

    try:
        body_json: dict = json.loads(request.body)
    except Exception as exc:
        return JsonResponseBadRequest({"error": f"Could not parse request: {str(exc)}"})

    response_form = AuthenticationResponseForm(body_json)

    if not response_form.is_valid():
        return JsonResponseBadRequest(dict(response_form.errors.items()))

    form_data = response_form.cleaned_data
    options_username: str | None = form_data["username"]
    options_webauthn_response: dict = form_data["response"]

    authentication_service = AuthenticationService()
    credential_service = CredentialService()
    session_service = SessionService()

    try:
        existing_credential = credential_service.retrieve_credential_by_id(
            credential_id=options_webauthn_response["id"],
            username=options_username,
        )

        verification = authentication_service.verify_authentication_response(
            cache_key=session_service.get_session_key(session=request.session),
            existing_credential=existing_credential,
            response=options_webauthn_response,
        )

        # Update credential with new sign count
        credential_service.update_credential_sign_count(verification=verification)
    except Exception as err:
        return JsonResponseBadRequest({"error": str(err)})

    session_service.log_in_user(session=request.session, username=verification.username)

    return JsonResponse({"verified": True})
