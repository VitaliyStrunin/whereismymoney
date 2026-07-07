from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.tag import Tag


class TagRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, name: str, user_id: int) -> Tag:
        tag = Tag(name=name, user_id=user_id)
        self.session.add(tag)
        self.session.flush()
        return tag

    def get_by_id(self, tag_id: int, user_id: int) -> Tag | None:
        query = select(Tag).where(Tag.id == tag_id, Tag.user_id == user_id)
        tag = self.session.scalar(query)
        return tag

    def get_by_ids(self, tag_ids: list[int], user_id: int) -> list[Tag]:
        if not tag_ids:
            return []

        query = select(Tag).where(Tag.id.in_(set(tag_ids)), Tag.user_id == user_id)
        return list(self.session.scalars(query))

    def get_list(self, limit: int, offset: int, user_id: int) -> list[Tag]:
        query = (select(Tag)
                 .where(Tag.user_id == user_id)
                 .order_by(Tag.id)
                 .limit(limit)
                 .offset(offset)
                 )
        return list(self.session.scalars(query))

    def update(self, tag: Tag, name: str) -> Tag:
        tag.name = name
        self.session.flush()
        return tag

    def delete(self, tag: Tag) -> None:
        self.session.delete(tag)
        self.session.flush()
