from django.shortcuts import render, redirect

from homepage.const import libraries
from homepage.services import SessionService


def profile(request):
    """
    Render the logged-in user's "profile" page
    """
    session_service = SessionService()

    if not session_service.user_is_logged_in(request=request):
        return redirect("index")

    context = {
        "libraries": libraries,
    }

    return render(request, "homepage/profile.html", context)
