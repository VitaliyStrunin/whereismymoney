from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.db import Base


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True, nullable=False)
    expenses = relationship("Expense", back_populates="tags", secondary="expense_tags")
