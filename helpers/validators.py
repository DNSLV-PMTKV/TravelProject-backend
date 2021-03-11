import re

EMAIL_RE = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,5}$'


def email_is_correct(email: str) -> bool:
    if re.search(EMAIL_RE, email):
        return True
    return False
