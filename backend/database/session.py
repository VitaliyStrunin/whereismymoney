from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings


def create_session_factory(database_url: str):
    engine = create_engine(database_url)
    return sessionmaker(engine, expire_on_commit=False)


session_maker = create_session_factory(settings.db_url)
