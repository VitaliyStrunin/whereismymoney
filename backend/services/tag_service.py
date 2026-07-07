from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.core.exceptions import TagAlreadyExistsError, TagNotFoundError
from backend.models.tag import Tag
from backend.repositories.tag_repository import TagRepository


class TagService:
    def __init__(self, session: Session):
        self.session = session
        self.tag_repo = TagRepository(session)

    def create_tag(self, name: str, user_id: int) -> Tag:
        try:
            tag = self.tag_repo.create(name=name, user_id=user_id)
            self.session.commit()
            return tag
        except IntegrityError as err:
            self.session.rollback()
            raise TagAlreadyExistsError from err
        except Exception:
            self.session.rollback()
            raise

    def get_by_id(self, tag_id: int, user_id: int) -> Tag:
        tag = self.tag_repo.get_by_id(tag_id=tag_id, user_id=user_id)
        if tag is None:
            raise TagNotFoundError(f"Tag with id {tag_id} is not found")
        return tag

    def get_by_ids(self, tag_ids: list[int], user_id: int) -> list[Tag]:
        tags = self.tag_repo.get_by_ids(tag_ids=tag_ids, user_id=user_id)
        return tags

    def get_list(self, limit: int, offset: int, user_id) -> list[Tag]:
        tags = self.tag_repo.get_list(limit=limit, offset=offset, user_id=user_id)
        return tags

    def update_tag(self, tag_id: int, name: str, user_id: int) -> Tag:
        try:
            tag = self.get_by_id(tag_id=tag_id, user_id=user_id)
            updated_tag = self.tag_repo.update(tag=tag, name=name)
            self.session.commit()
            return updated_tag
        except IntegrityError as err:
            self.session.rollback()
            raise TagAlreadyExistsError from err
        except Exception:
            self.session.rollback()
            raise

    def delete_tag(self, tag_id: int, user_id: int) -> None:
        try:
            tag = self.get_by_id(tag_id=tag_id, user_id=user_id)
            self.tag_repo.delete(tag)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
