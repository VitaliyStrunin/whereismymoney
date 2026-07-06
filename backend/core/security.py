from datetime import datetime, timedelta, timezone

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from werkzeug.security import check_password_hash, generate_password_hash

from backend.core.config import settings
from backend.core.exceptions import AccessTokenExpiredError, InvalidAccessTokenError


def hash_password(plain_password: str) -> str:
    return generate_password_hash(plain_password, method="scrypt")


def verify_password(password_hash: str, plain_password: str) -> bool:
    return check_password_hash(password_hash, plain_password)


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_TTL_MINUTES)
    }

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        if payload.get("type") != "access":
            raise InvalidAccessTokenError

        user_id = int(payload['sub'])

        if user_id <= 0:
            raise InvalidAccessTokenError

        return user_id
    except ExpiredSignatureError as err:
        raise AccessTokenExpiredError from err
    except (InvalidTokenError, KeyError, TypeError, ValueError) as err:
        raise InvalidAccessTokenError from err
