from sqlalchemy.orm import Session

from backend.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from backend.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from backend.models.user import User
from backend.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)

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


    def login(self, email: str, plain_password: str) -> str:
        user = self.user_repo.get_by_email(email)

        if user is None:
            raise InvalidCredentialsError

        password_correct = verify_password(user.password_hash, plain_password)

        if not password_correct:
            raise InvalidCredentialsError

        access_token = create_access_token(user.id)

        return access_token


    def get_user_by_id(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError

        return user
