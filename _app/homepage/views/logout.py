from django.shortcuts import redirect
from django.http import HttpRequest

from homepage.services import SessionService


def logout(request: HttpRequest):
    session_service = SessionService()
    session_service.log_out_user(session=request.session)
    return redirect("index")
