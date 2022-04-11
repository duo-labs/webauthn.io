from django.shortcuts import render

from .forms import UsernameForm


def index(request):
    """
    Render the homepage
    """
    username_form = UsernameForm()

    return render(request, "homepage/index.html", {"username_form": username_form})
