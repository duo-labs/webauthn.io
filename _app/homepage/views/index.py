from django.shortcuts import render

from homepage.const import libraries
from homepage.services import SessionService


def index(request):
    """
    Render the homepage
    """
    context = {
        "libraries": libraries,
    }

    session_service = SessionService()

    template = "homepage/index.html"
    if session_service.user_is_logged_in(request=request):
        template = "homepage/profile.html"

    return render(request, template, context)
