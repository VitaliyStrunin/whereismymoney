from collections.abc import Iterator
from contextlib import contextmanager

from flask import current_app, request
from sqlalchemy.orm import Session

from backend.core.exceptions import (
    InvalidAccessTokenError,
)
from backend.core.security import decode_access_token


@contextmanager
def get_db_session() -> Iterator[Session]:
    session_factory = current_app.extensions['session_factory']

    with session_factory() as session:
        yield session


def _get_access_token_from_request() -> str | None:
    auth_header = request.headers.get("Authorization")

    if auth_header is None:
        return None

    scheme, _, token = auth_header.partition(" ")

    if scheme.lower() != "bearer" or not token.strip():
        return None

    return token.strip()


def get_current_user_id() -> int:
    access_token = _get_access_token_from_request()
    if access_token is None:
        raise InvalidAccessTokenError

    user_id = decode_access_token(access_token)

    return user_id
