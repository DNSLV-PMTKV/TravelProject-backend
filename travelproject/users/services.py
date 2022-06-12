from typing import Any, Dict

from django.db.models.query import QuerySet
from rest_framework.serializers import ValidationError

from travelproject.common.services import model_update
from travelproject.users.messages import (
    OLD_PASSWORD_IS_NOT_VALID,
    USER_ALREADY_EXISTS,
    USER_PASSWORDS_NOT_MATCH,
)
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

    # TODO: send confirmation email

    return user


def user_list() -> QuerySet[User]:
    return User.objects.filter(is_active=True)


def user_update(*, user: User, data: Dict[str, Any]) -> User:
    fields = ["first_name", "last_name", "email"]

    user, _ = model_update(
        instance=user, fields=fields, data=data, exclude=["password"]
    )

    return user


def user_delete(*, user: User):
    user.delete()


def user_change_password(
    *, user: User, old_password: str, new_password: str, re_password: str
):
    if not user.check_password(old_password):
        raise ValidationError(OLD_PASSWORD_IS_NOT_VALID)

    if new_password != re_password:
        raise ValidationError(USER_PASSWORDS_NOT_MATCH)

    user.set_password(new_password)
    user.save()
