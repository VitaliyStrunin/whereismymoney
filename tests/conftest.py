from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from alembic import command
from backend.core.config import settings
from backend.core.security import create_access_token, hash_password
from backend.main import create_app
from backend.models.category import Category
from backend.models.expense import Expense
from backend.models.expense_tags import expense_tags
from backend.models.tag import Tag
from backend.models.user import User


@pytest.fixture(scope="session")
def test_database_url() -> str:
    if settings.test_db_url == settings.db_url:
        pytest.fail("test_db_url must not be equal to db_url")

    return settings.test_db_url


@pytest.fixture(scope="session")
def test_engine(test_database_url: str):
    engine = create_engine(test_database_url)

    alembic_cfg = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", test_database_url)

    command.upgrade(alembic_cfg, "head")

    yield engine

    engine.dispose()


@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    return sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest.fixture
def app(test_session_factory):
    app = create_app(session_factory=test_session_factory)
    app.config.update(TESTING=True)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db(test_session_factory):
    yield

    with test_session_factory() as session:
        session.execute(expense_tags.delete())
        session.query(Expense).delete()
        session.query(Tag).delete()
        session.query(Category).delete()
        session.query(User).delete()

        session.commit()


@pytest.fixture
def create_category(test_session_factory, default_user):
    def _create_category(name: str | None = None, user: User | None = None) -> Category:
        user = user or default_user
        name = name or f"cat-{uuid4().hex}"

        with test_session_factory() as session:
            user = session.merge(user)
            category = Category(name=name, user=user)
            session.add(category)
            session.commit()
            session.refresh(category)
            return category

    return _create_category


@pytest.fixture
def create_tag(test_session_factory, default_user):
    def _create_tag(name: str | None = None, user: User | None = None) -> Tag:
        user = user or default_user
        name = name or f"tag-{uuid4().hex}"

        with test_session_factory() as session:
            user = session.merge(user)
            tag = Tag(name=name, user=user)
            session.add(tag)
            session.commit()
            session.refresh(tag)
            return tag

    return _create_tag


@pytest.fixture
def create_expense(test_session_factory,
                   create_category,
                   create_tag,
                   default_user):
    def _create_expense(
        amount: Decimal = Decimal("100.0"),
        description: str | None = None,
        expense_date: date = date(1970, 1, 1),
        category: Category | None = None,
        tags: list[Tag] | None = None,
        user: User | None = None
        ) -> Expense:

        user = user or default_user

        if category is None:
            category = create_category(user=user)

        if tags is None:
            tags = [create_tag(user=user), create_tag(user=user)]


        description = description or f"desc-{uuid4().hex}"

        with test_session_factory() as session:
            category = session.merge(category)
            tags = [session.merge(tag) for tag in tags]
            user = session.merge(user)

            expense = Expense(
                amount=amount,
                description=description,
                expense_date=expense_date,
                category=category,
                tags=tags,
                user=user
            )

            session.add(expense)
            session.commit()
            session.refresh(expense)

            return expense

    return _create_expense


@pytest.fixture
def create_user(test_session_factory):
    def _create_user(
        email: str = "testemail@gmail.com",
        plain_password: str = "SomePlainPassword"
    ):
        with test_session_factory() as session:
            user = User(
                email=email,
                password_hash=hash_password(plain_password=plain_password)
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    return _create_user


@pytest.fixture
def default_user(create_user):
    return create_user()


@pytest.fixture
def default_user_auth_headers(default_user, make_auth_headers):
    return make_auth_headers(default_user)


@pytest.fixture
def make_auth_headers():
    def _make_auth_headers(user: User):
        access_token = create_access_token(user.id)
        return {"Authorization": f"Bearer {access_token}"}
    return _make_auth_headers
