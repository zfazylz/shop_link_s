from typing import Optional

import graphene
import jwt
from django.core.exceptions import ValidationError
from django.middleware.csrf import (  # type: ignore
    _compare_masked_tokens,
    _get_new_csrf_token,
)
from django.utils import timezone
from django.utils.crypto import get_random_string
from graphene.types.generic import GenericScalar

from ....account import models
from ....account.error_codes import AccountErrorCode
from ....account.validators import validate_phone_number_as_field
from ....core.jwt import (
    JWT_REFRESH_TOKEN_COOKIE_NAME,
    JWT_REFRESH_TYPE,
    PERMISSIONS_FIELD,
    create_access_token,
    create_refresh_token,
    get_user_from_payload,
    jwt_decode,
)
from ....core.permissions import get_permissions_from_names
from ...core.mutations import BaseMutation
from ...core.types.common import AccountError
from ..types import User
from ....sms.utils import verify_sms_code


def get_payload(token):
    try:
        payload = jwt_decode(token)
    except jwt.ExpiredSignature:
        raise ValidationError(
            "Signature has expired", code=AccountErrorCode.JWT_SIGNATURE_EXPIRED.value
        )
    except jwt.DecodeError:
        raise ValidationError(
            "Error decoding signature", code=AccountErrorCode.JWT_DECODE_ERROR.value
        )
    except jwt.InvalidTokenError:
        raise ValidationError(
            "Invalid token", code=AccountErrorCode.JWT_INVALID_TOKEN.value
        )
    return payload


def get_user(payload):
    try:
        user = get_user_from_payload(payload)
    except Exception:
        user = None
    if not user:
        raise ValidationError(
            "Invalid token", code=AccountErrorCode.JWT_INVALID_TOKEN.value
        )
    permissions = payload.get(PERMISSIONS_FIELD)
    if permissions is not None:
        user.effective_permissions = get_permissions_from_names(permissions)
    return user


class TokenMutationMixin:
    token = graphene.String(description="JWT token, required to authenticate.")
    refresh_token = graphene.String(
        description="JWT refresh token, required to re-generate access token."
    )
    csrf_token = graphene.String(
        description="CSRF token required to re-generate access token."
    )

    @classmethod
    def get_access_token(cls, user):
        return create_access_token(user)

    @classmethod
    def get_csrf_token(cls):
        return _get_new_csrf_token()

    @classmethod
    def get_refresh_token(cls, user, csrf_token):
        return create_refresh_token(user, {"csrfToken": csrf_token})


class CreateToken(BaseMutation, TokenMutationMixin):
    """Mutation that authenticates a user and returns token and user data."""

    class Arguments:
        phone = graphene.String(required=True, description="Phone number of a user.")
        sms_code = graphene.String(required=True, description="SMS code.")

    class Meta:
        description = "Create JWT token."
        error_type_class = AccountError
        error_type_field = "account_errors"

    user = graphene.Field(User, description="A user instance.")

    @classmethod
    def _get_user(cls, phone) -> Optional[models.User]:
        user = models.User.objects.filter(phone=phone).first()
        if user is None:
            # TEMP solution to allow user to do anything
            user = models.User.objects.create_user(
                phone=phone,
                is_superuser=True,
                is_staff=True,
            )
        if user and user.is_active:
            return user

    @classmethod
    def _verify_sms_code(cls, phone, sms_code):
        return verify_sms_code(phone, sms_code)

    @classmethod
    def get_user(cls, _info, data):
        phone = data["phone"]
        validate_phone_number_as_field(phone)
        user = cls._get_user(phone)
        if not user:
            raise ValidationError(
                {
                    "phone": ValidationError(
                        "Phone number not found",
                        code=AccountErrorCode.NOT_FOUND.value,
                    )
                }
            )
        if not cls._verify_sms_code(data["phone"], data["sms_code"]):
            raise ValidationError(
                {
                    "sms_code": ValidationError(
                        "Please, enter valid SMS code",
                        code=AccountErrorCode.INVALID_CREDENTIALS.value,
                    )
                }
            )
        return user

    @classmethod
    def perform_mutation(cls, root, info, **data):
        user = cls.get_user(info, data)
        access_token = cls.get_access_token(user)
        csrf_token = cls.get_csrf_token()
        refresh_token = cls.get_refresh_token(user, csrf_token)
        info.context.refresh_token = refresh_token
        info.context._cached_user = user
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return cls(
            errors=[],
            user=user,
            token=access_token,
            refresh_token=refresh_token,
            csrf_token=csrf_token,
        )


class RefreshToken(BaseMutation):
    """Mutation that refresh user token and returns token and user data."""

    token = graphene.String(description="JWT token, required to authenticate.")
    user = graphene.Field(User, description="A user instance.")

    class Arguments:
        refresh_token = graphene.String(required=False, description="Refresh token.")
        csrf_token = graphene.String(
            required=False,
            description=(
                "CSRF token required to refresh token. This argument is "
                "required when refreshToken is provided as a cookie."
            ),
        )

    class Meta:
        description = (
            "Refresh JWT token. Mutation tries to take refreshToken from the input."
            "If it fails it will try to take refreshToken from the http-only cookie -"
            f"{JWT_REFRESH_TOKEN_COOKIE_NAME}. csrfToken is required when refreshToken "
            "is provided as a cookie."
        )
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def get_refresh_token_payload(cls, refresh_token):
        try:
            payload = get_payload(refresh_token)
        except ValidationError as e:
            raise ValidationError({"refreshToken": e})
        return payload

    @classmethod
    def get_refresh_token(cls, info, data):
        request = info.context
        refresh_token = request.COOKIES.get(JWT_REFRESH_TOKEN_COOKIE_NAME, None)
        refresh_token = data.get("refresh_token") or refresh_token
        return refresh_token

    @classmethod
    def clean_refresh_token(cls, refresh_token):
        if not refresh_token:
            raise ValidationError(
                {
                    "refreshToken": ValidationError(
                        "Missing refreshToken",
                        code=AccountErrorCode.JWT_MISSING_TOKEN.value,
                    )
                }
            )
        payload = cls.get_refresh_token_payload(refresh_token)
        if payload["type"] != JWT_REFRESH_TYPE:
            raise ValidationError(
                {
                    "refreshToken": ValidationError(
                        "Incorrect refreshToken",
                        code=AccountErrorCode.JWT_INVALID_TOKEN.value,
                    )
                }
            )
        return payload

    @classmethod
    def clean_csrf_token(cls, csrf_token, payload):
        is_valid = _compare_masked_tokens(csrf_token, payload["csrfToken"])
        if not is_valid:
            raise ValidationError(
                {
                    "csrfToken": ValidationError(
                        "Invalid csrf token",
                        code=AccountErrorCode.JWT_INVALID_CSRF_TOKEN.value,
                    )
                }
            )

    @classmethod
    def get_user(cls, payload):
        try:
            user = get_user(payload)
        except ValidationError as e:
            raise ValidationError({"refreshToken": e})
        return user

    @classmethod
    def perform_mutation(cls, root, info, **data):
        refresh_token = cls.get_refresh_token(info, data)
        payload = cls.clean_refresh_token(refresh_token)

        # None when we got refresh_token from cookie.
        if not data.get("refresh_token"):
            csrf_token = data.get("csrf_token")
            cls.clean_csrf_token(csrf_token, payload)

        user = get_user(payload)
        token = create_access_token(user)
        return cls(errors=[], user=user, token=token)


class VerifyToken(BaseMutation):
    """Mutation that confirms if token is valid and also returns user data."""

    user = graphene.Field(User, description="User assigned to token.")
    is_valid = graphene.Boolean(
        required=True,
        default_value=False,
        description="Determine if token is valid or not.",
    )
    payload = GenericScalar(description="JWT payload.")

    class Arguments:
        token = graphene.String(required=True, description="JWT token to validate.")

    class Meta:
        description = "Verify JWT token."
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def get_payload(cls, token):
        try:
            payload = get_payload(token)
        except ValidationError as e:
            raise ValidationError({"token": e})
        return payload

    @classmethod
    def get_user(cls, payload):
        try:
            user = get_user(payload)
        except ValidationError as e:
            raise ValidationError({"token": e})
        return user

    @classmethod
    def perform_mutation(cls, root, info, **data):
        token = data["token"]
        payload = cls.get_payload(token)
        user = cls.get_user(payload)
        return cls(errors=[], user=user, is_valid=True, payload=payload)


class DeactivateAllUserTokens(BaseMutation):
    class Meta:
        description = "Deactivate all JWT tokens of the currently authenticated user."
        error_type_class = AccountError
        error_type_field = "account_errors"

    @classmethod
    def check_permissions(cls, context):
        return context.user.is_authenticated

    @classmethod
    def perform_mutation(cls, root, info, **data):
        user = info.context.user
        user.jwt_token_key = get_random_string()
        user.save(update_fields=["jwt_token_key"])
        return cls()
