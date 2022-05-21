from rest_framework.serializers import ValidationError

from travelproject.users.messages import USER_ALREADY_EXISTS, USER_PASSWORDS_NOT_MATCH
from travelproject.users.models import User


def user_create(
    *, email: str, first_name: str, last_name: str, password: str, re_password: str
) -> User:
    user_exists = User.objects.filter(email=email).exists()
    if user_exists:
        raise ValidationError(USER_ALREADY_EXISTS)

    if password != re_password:
        raise ValidationError(USER_PASSWORDS_NOT_MATCH)

    user = User(first_name=first_name, last_name=last_name, email=email)
    user.set_password(password)

    return user
