from django.shortcuts import render
from webauthn.helpers.structs import CredentialDeviceType

from homepage.const import libraries, demos
from homepage.logging import logger
from homepage.services import SessionService, CredentialService, MetadataService
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
        metadata_service = MetadataService()

        user_credentials = credential_service.retrieve_credentials_by_username(username=username)

        parsed_credentials = []

        for cred in user_credentials:
            description = ""

            if cred.device_type == CredentialDeviceType.SINGLE_DEVICE:
                description += "device-bound "
            else:
                description += "synced "

            if cred.is_discoverable_credential is None:
                # We can't really describe it if we didn't get a signal back
                description += "credential of unknown discoverability"
            elif cred.is_discoverable_credential:
                description += "passkey"
            else:
                description += "non-discoverable credential"

            aaguid = str(cred.aaguid)
            provider_name = metadata_service.get_provider_name(
                aaguid=aaguid,
                device_type=cred.device_type,
            )

            parsed_credentials.append(
                {
                    "id": truncate_credential_id_to_ui_string(cred.id),
                    "raw_id": cred.id,
                    "transports": transports_to_ui_string(cred.transports or []),
                    "description": description,
                    "provider_name": provider_name,
                    "aaguid": aaguid,
                }
            )

        context["credentials"] = parsed_credentials

    return render(request, template, context)
