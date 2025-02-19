from django.http import HttpRequest
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from homepage.const import libraries, demos
from homepage.services import SessionService


@never_cache
def index(request: HttpRequest):
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
