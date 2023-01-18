from django.shortcuts import render

from homepage.const import libraries, demos
from homepage.services import SessionService, CredentialService
from homepage.helpers import transports_to_ui_string, truncate_credential_id_to_ui_string


def index(request):
    """
    Render the homepage
    """
    context = {
        "libraries": libraries,
        "demos": demos,
    }

    session_service = SessionService()
    session_service.start_session(request=request)

    template = "homepage/index.html"
    if session_service.user_is_logged_in(request=request):
        template = "homepage/profile.html"

        username = request.session["username"]
        credential_service = CredentialService()

        user_credentials = credential_service.retrieve_credentials_by_username(username=username)

        parsed_credentials = []

        for cred in user_credentials:
            description = ""

            if cred.device_type == "single_device":
                description += "single-device "

            if cred.is_discoverable_credential:
                description += "passkey"
            else:
                description += "non-discoverable credential"

            parsed_credentials.append(
                {
                    "id": truncate_credential_id_to_ui_string(cred.id),
                    "raw_id": cred.id,
                    "transports": transports_to_ui_string(cred.transports or []),
                    "description": description,
                }
            )

        context["credentials"] = parsed_credentials

    return render(request, template, context)
