from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.exceptions import (
    CategoryAlreadyExistsError,
    CategoryInUseError,
    CategoryNotFoundError,
)
from backend.models.category import Category
from backend.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, session: Session):
        self.session = session
        self.category_repo = CategoryRepository(session)

    def create_category(self, name: str, user_id: int) -> Category:
        try:
            category = self.category_repo.create(name=name, user_id=user_id)
            self.session.commit()
            return category
        except IntegrityError as err:
            self.session.rollback()
            raise CategoryAlreadyExistsError from err
        except Exception:
            self.session.rollback()
            raise

    def get_by_id(self, category_id: int, user_id: int) -> Category:
        category = self.category_repo.get_by_id(category_id=category_id, user_id=user_id)
        if category is None:
            raise CategoryNotFoundError(f"Category with id {category_id} not found")
        return category

    def get_list(self, limit: int, offset: int, user_id: int) -> list[Category]:
        categories = self.category_repo.get_list(limit=limit, offset=offset, user_id=user_id)
        return categories

    def update_category(self, category_id: int, name: str, user_id: int) -> Category:
        try:
            category = self.get_by_id(category_id=category_id, user_id=user_id)
            updated_category = self.category_repo.update(category, name)
            self.session.commit()
            return updated_category
        except IntegrityError as err:
            self.session.rollback()
            raise CategoryAlreadyExistsError from err
        except Exception:
            self.session.rollback()
            raise

    def delete_category(self, category_id: int, user_id: int) -> None:
        try:
            category = self.get_by_id(category_id=category_id, user_id=user_id)
            self.category_repo.delete(category)
            self.session.commit()
        except IntegrityError as err:
            self.session.rollback()
            raise CategoryInUseError("Category is used by expenses") from err
        except Exception:
            self.session.rollback()
            raise
