from django.shortcuts import render

from homepage.forms import UsernameForm
from homepage.const import libraries


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
