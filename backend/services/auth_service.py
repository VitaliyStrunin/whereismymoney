from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.exceptions import (
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from backend.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from backend.models.user import User
from backend.repositories.refresh_session_repository import RefreshSessionRepository
from backend.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.refresh_session_repo = RefreshSessionRepository(session)

    def register(self, email: str, plain_password: str) -> User:
        user_exists = self.user_repo.get_by_email(email) is not None

        if user_exists:
            raise UserAlreadyExistsError

        password_hash = hash_password(plain_password)

        try:
            created_user = self.user_repo.create(email, password_hash)
            self.session.commit()
            return created_user
        except Exception:
            self.session.rollback()
            raise


    def login(self, email: str, plain_password: str) -> tuple[str, str]:
        user = self.user_repo.get_by_email(email)

        if user is None:
            raise InvalidCredentialsError

        password_correct = verify_password(user.password_hash, plain_password)

        if not password_correct:
            raise InvalidCredentialsError

        try:
            access_token = create_access_token(user.id)
            refresh_token = self._create_refresh_token(user.id)
            self.session.commit()
            return access_token, refresh_token

        except Exception:
            self.session.rollback()
            raise

    def _create_refresh_token(self, user_id: int) -> str:
        raw_refresh_token = generate_refresh_token()
        token_hash = hash_refresh_token(raw_refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_TTL_DAYS)
        self.refresh_session_repo.create(user_id=user_id, token_hash=token_hash, expires_at=expires_at)

        return raw_refresh_token

    def refresh(self, raw_refresh_token: str) -> tuple[str, str]:
        if not raw_refresh_token:
            raise InvalidRefreshTokenError

        token_hash = hash_refresh_token(raw_refresh_token)
        refresh_session = self.refresh_session_repo.get_active_by_token_hash(token_hash)

        if refresh_session is None:
            raise InvalidRefreshTokenError

        try:
            self.refresh_session_repo.revoke(refresh_session)
            access_token = create_access_token(refresh_session.user_id)
            refresh_token = self._create_refresh_token(refresh_session.user_id)
            self.session.commit()
            return access_token, refresh_token
        except Exception:
            self.session.rollback()
            raise

    def logout(self, raw_refresh_token: str | None) -> None:
        if not raw_refresh_token:
            raise InvalidRefreshTokenError

        token_hash = hash_refresh_token(raw_refresh_token)
        refresh_session = self.refresh_session_repo.get_active_by_token_hash(token_hash)

        if refresh_session is None:
            return

        try:
            self.refresh_session_repo.revoke(refresh_session)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def get_user_by_id(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError

        return user

