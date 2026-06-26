from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.db import Base


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True, nullable=False)
    expenses = relationship("Expense", back_populates="category")
