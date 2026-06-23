from sqlalchemy import Column, ForeignKey, Table

from backend.database.db import Base

expense_tags = Table(
    "expense_tags",
    Base.metadata,
    Column("expense_id", ForeignKey("expenses.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
