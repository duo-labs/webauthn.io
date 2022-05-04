from django.shortcuts import render

from homepage.const import libraries


def profile(request):
    """
    Render the logged-in user's "profile" page
    """
    context = {
        "libraries": libraries,
    }

    return render(request, "homepage/profile.html", context)
