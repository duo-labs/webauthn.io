from django.shortcuts import redirect

from homepage.services import SessionService


def logout(request):
    session_service = SessionService()
    session_service.log_out_user(request=request)
    return redirect("index")
