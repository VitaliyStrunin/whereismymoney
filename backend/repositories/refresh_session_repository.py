from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.refresh_session import RefreshSession


class RefreshSessionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_id: int, token_hash: str, expires_at: datetime) -> RefreshSession:
        refresh_session = RefreshSession(user_id=user_id, token_hash=token_hash, expires_at=expires_at)

        self.session.add(refresh_session)
        self.session.flush()

        return refresh_session


    def get_active_by_token_hash(self, token_hash: str) -> RefreshSession | None:
        now = datetime.now(timezone.utc)

        query = (
            select(RefreshSession)
            .where(RefreshSession.token_hash == token_hash,
                   RefreshSession.revoked_at.is_(None),
                   RefreshSession.expires_at > now)
        )

        return self.session.scalar(query)


    def revoke(self, refresh_session: RefreshSession) -> RefreshSession:
        refresh_session.revoked_at = datetime.now(timezone.utc)
        self.session.flush()

        return refresh_session
