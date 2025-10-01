from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from webauthn.helpers import decode_credential_public_key, base64url_to_bytes
from webauthn.helpers.cose import COSEKTY, COSEAlgorithmIdentifier
from webauthn.helpers.structs import CredentialDeviceType

from homepage.services import SessionService, CredentialService, MetadataService
from homepage.helpers import (
    transports_to_ui_string,
    truncate_credential_id_to_ui_string,
)
from homepage.cookies import get_debug_cookie_name, get_debug_cookie_expiration


@never_cache
def profile(request: HttpRequest):
    """
    Render the logged-in profile page, including list of credentials
    """
    session_service = SessionService()

    if not session_service.user_is_logged_in(session=request.session):
        return redirect("index")

    template = "homepage/profile.html"

    username = request.session["username"]
    credential_service = CredentialService()
    metadata_service = MetadataService()

    cookie_debug = request.COOKIES.get(get_debug_cookie_name())
    query_debug = request.GET.get("debug")

    show_debug_info = False
    if cookie_debug == "true":
        # Show additional information when the debug cookie is set
        show_debug_info = True
    elif query_debug == "true":
        # Enable adding ?debug=true to the URL to show additional information
        show_debug_info = True

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

        if not provider_name:
            provider_name = "(Unavailable)"

        if not aaguid:
            aaguid = "(Unavailable)"

        debug_info = None
        if show_debug_info:
            decoded_pub_key = decode_credential_public_key(base64url_to_bytes(cred.public_key))

            # Make kty and alg sensible for human consumption
            kty = f"{COSEKTY(decoded_pub_key.kty).name} ({decoded_pub_key.kty})"
            alg = f"{COSEAlgorithmIdentifier(decoded_pub_key.alg).name} ({decoded_pub_key.alg})"

            normalized_kty = kty.replace("_", "-")
            normalized_alg = alg.replace("_", "-")

            debug_info = {
                "public_key": {
                    "kty": normalized_kty,
                    "alg": normalized_alg,
                }
            }

        parsed_credentials.append(
            {
                "id": truncate_credential_id_to_ui_string(cred.id),
                "raw_id": cred.id,
                "transports": transports_to_ui_string(cred.transports or []),
                "description": description,
                "provider_name": provider_name,
                "aaguid": aaguid,
                "debug_info": debug_info,
            }
        )

    context = {
        "credentials": parsed_credentials,
    }

    response = render(request, template, context)

    if show_debug_info:
        response.set_cookie(
            key=get_debug_cookie_name(),
            value="true",
            expires=get_debug_cookie_expiration(),
        )

    return response
