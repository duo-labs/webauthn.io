from django.contrib.sessions.backends.base import SessionBase


class SessionService:
    def start_session(self, *, session: SessionBase) -> None:
        """
        Start a session so that we have a unique ID we can associate options with, even when
        we don't have a username
        """
        if not session.exists(session.session_key):
            session.create()
            session.set_expiry(0)

    def log_in_user(self, *, session: SessionBase, username: str) -> None:
        """
        Use a session cookie to temporarily remember the user
        """
        session["username"] = username
        session.save()

    def log_out_user(self, *, session: SessionBase) -> None:
        """
        Annihilate the user's session so we can forget about them
        """
        session.flush()

    def user_is_logged_in(self, *, session: SessionBase) -> bool:
        try:
            username = session["username"]
            return username is not None
        except KeyError:
            pass

        return False

    def get_session_key(self, *, session: SessionBase) -> str:
        key = session.session_key

        if not key:
            raise Exception("Attempted to get session key before session was created")

        return key
