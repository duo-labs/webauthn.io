from django.shortcuts import render

from homepage.const import libraries, demos
from homepage.services import SessionService


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

    return render(request, template, context)
