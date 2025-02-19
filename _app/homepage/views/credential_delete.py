from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from homepage.services import CredentialService


@require_http_methods(["POST"])
def credential_delete(request, credential_id):
    credential_service = CredentialService()
    credential_service.delete_credential_by_id(credential_id=credential_id)
    return JsonResponse({"deleted": True})
