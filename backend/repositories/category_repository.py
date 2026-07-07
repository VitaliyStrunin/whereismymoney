from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.category import Category


class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, name: str, user_id: int) -> Category:
        category = Category(name=name, user_id=user_id)
        self.session.add(category)
        self.session.flush()
        return category

    def get_by_id(self, category_id: int, user_id: int) -> Category | None:
        query = select(Category).where(Category.id == category_id, Category.user_id == user_id)
        category = self.session.scalar(query)
        return category

    def get_list(self, limit: int, offset: int, user_id: int) -> list[Category]:
        query = (select(Category)
                 .where(Category.user_id == user_id)
                 .order_by(Category.id)
                 .limit(limit)
                 .offset(offset)
                 )
        return list(self.session.scalars(query))

    def update(self, category: Category, name: str) -> Category:
        category.name = name
        self.session.flush()
        return category

    def delete(self, category: Category) -> None:
        self.session.delete(category)
        self.session.flush()
