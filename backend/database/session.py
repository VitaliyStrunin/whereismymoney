from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.core.config import settings

engine = create_engine(settings.db_url)

session_maker = sessionmaker(engine, expire_on_commit=False)


def get_db_session() -> Generator[Session, None, None]:
    with session_maker() as session:
        yield session
