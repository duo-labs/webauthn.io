from django.http import JsonResponse


class JsonResponseBadRequest(JsonResponse):
    """
    A variation of Django's JsonResponse indicating that bad arguments were sent
    """

    status_code = 400
