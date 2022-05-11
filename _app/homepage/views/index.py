from django.shortcuts import render

from homepage.const import libraries


def index(request):
    """
    Render the homepage
    """
    context = {
        "libraries": libraries,
    }

    return render(request, "homepage/index.html", context)
