from django.shortcuts import render


def index(request):
    """
    Render the homepage
    """
    return render(request, "homepage/index.html")
