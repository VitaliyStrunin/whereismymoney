from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.tag import Tag


class TagRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, name: str) -> Tag:
        tag = Tag(name=name)
        self.session.add(tag)
        self.session.flush()
        return tag

    def get_by_id(self, tag_id: int) -> Tag | None:
        tag = self.session.get(Tag, tag_id)
        return tag

    def get_by_ids(self, tag_ids: list[int]) -> list[Tag]:
        if not tag_ids:
            return []

        query = select(Tag).where(Tag.id.in_(set(tag_ids)))
        return list(self.session.scalars(query))

    def get_list(self, limit: int = 100, offset: int = 0) -> list[Tag]:
        query = select(Tag).order_by(Tag.id).limit(limit).offset(offset)
        return list(self.session.scalars(query))

    def update(self, tag: Tag, name: str) -> Tag:
        tag.name = name
        self.session.flush()
        return tag

    def delete(self, tag: Tag) -> None:
        self.session.delete(tag)
        self.session.flush()
