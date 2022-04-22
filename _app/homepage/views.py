from django.shortcuts import render

from .forms import UsernameForm
from .const import libraries


def index(request):
    """
    Render the homepage
    """
    username_form = UsernameForm()
    context = {
        "username_form": username_form,
        "libraries": libraries,
    }

    return render(request, "homepage/index.html", context)


def profile(request):
    """
    Render the logged-in user's "profile" page
    """
    context = {
        "libraries": libraries,
    }

    return render(request, "homepage/profile.html", context)
