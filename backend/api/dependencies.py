from collections.abc import Iterator
from contextlib import contextmanager

from flask import current_app
from sqlalchemy.orm import Session


@contextmanager
def get_db_session() -> Iterator[Session]:
    session_factory = current_app.extensions['session_factory']

    with session_factory() as session:
        yield session
