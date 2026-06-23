from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.category import Category


class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, name: str) -> Category:
        category = Category(name=name)
        self.session.add(category)
        self.session.flush()
        return category

    def get_by_id(self, category_id: int) -> Category | None:
        category = self.session.get(Category, category_id)
        return category

    def get_list(self, limit: int = 100, offset: int = 0) -> list[Category]:
        query = select(Category).order_by(Category.id).limit(limit).offset(offset)
        return list(self.session.scalars(query))

    def update(self, category: Category, name: str) -> Category:
        category.name = name
        self.session.flush()
        return category

    def delete(self, category: Category) -> None:
        self.session.delete(category)
        self.session.flush()
