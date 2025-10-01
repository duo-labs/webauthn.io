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

    session_service = SessionService()
    session_service.start_session(session=request.session)

    template = "homepage/index.html"
    context = {
        "libraries": libraries,
        "demos": demos,
    }

    return render(request, template, context)
