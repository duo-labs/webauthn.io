from datetime import datetime


def get_debug_cookie_name() -> str:
    """
    Return the name of the debug cookie that reveals more info in various places
    """
    return "debug"


def get_debug_cookie_value() -> str:
    """
    Keeping things simple for now
    """
    return "true"


def get_debug_cookie_expiration() -> datetime:
    """
    Expires one year from now
    """
    _now = datetime.now()
    return datetime(
        year=(_now.year + 1),
        month=_now.month,
        day=_now.day,
    )
