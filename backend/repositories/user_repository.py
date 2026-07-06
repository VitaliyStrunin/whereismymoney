from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash)
        self.session.add(user)
        self.session.flush()
        return user

    def get_by_id(self, user_id: int) -> User | None:
        user = self.session.get(User, user_id)
        return user

    def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        user = self.session.scalar(query)
        return user

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.flush()
