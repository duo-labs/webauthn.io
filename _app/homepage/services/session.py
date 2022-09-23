from django.http import HttpRequest


class SessionService:
    def log_in_user(self, *, request: HttpRequest, username: str) -> None:
        """
        Use a session cookie to temporarily remember the user
        """
        request.session["username"] = username
        request.session.set_expiry(0)

    def log_out_user(self, *, request: HttpRequest) -> None:
        """
        Annihilate the user's session so we can forget about them
        """
        request.session.flush()

    def user_is_logged_in(self, *, request: HttpRequest) -> bool:
        try:
            username = request.session["username"]
            return username is not None
        except KeyError:
            pass

        return False
