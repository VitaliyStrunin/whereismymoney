from sqlalchemy.orm import Session

from backend.core.exceptions import TagNotFoundError
from backend.models.tag import Tag
from backend.repositories.tag_repository import TagRepository


class TagService:
    def __init__(self, session: Session):
        self.session = session
        self.tag_repo = TagRepository(session)

    def create_tag(self, name: str) -> Tag:
        try:
            tag = self.tag_repo.create(name)
            self.session.commit()
            return tag
        except Exception:
            self.session.rollback()
            raise

    def get_by_id(self, tag_id: int) -> Tag:
        tag = self.tag_repo.get_by_id(tag_id)
        if tag is None:
            raise TagNotFoundError(f"Tag with id {tag_id} is not found")
        return tag

    def get_by_ids(self, tag_ids: list[int]) -> list[Tag]:
        tags = self.tag_repo.get_by_ids(tag_ids)
        return tags

    def get_list(self, limit: int, offset: int) -> list[Tag]:
        tags = self.tag_repo.get_list(limit, offset)
        return tags

    def update_tag(self, tag_id: int, name: str) -> Tag:
        try:
            tag = self.get_by_id(tag_id)
            updated_tag = self.tag_repo.update(tag, name)
            self.session.commit()
            return updated_tag
        except Exception:
            self.session.rollback()
            raise

    def delete_tag(self, tag_id: int) -> None:
        try:
            tag = self.get_by_id(tag_id)
            self.tag_repo.delete(tag)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
