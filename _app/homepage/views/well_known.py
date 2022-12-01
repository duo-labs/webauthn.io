from django.http import JsonResponse
from django.conf import settings


def apple_app_site_association(request):
    """
    https://developer.apple.com/documentation/xcode/supporting-associated-domains
    """
    return JsonResponse(
        # https://developer.apple.com/documentation/authenticationservices/connecting_to_a_service_with_passkeys
        {"webcredentials": {"apps": [f"{settings.AASA_APP_ID_PREFIX}.{settings.AASA_BUNDLE_ID}"]}}
    )
