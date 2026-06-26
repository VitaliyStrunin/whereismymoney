from flask import Blueprint, jsonify, request

from backend.api.dependencies import get_db_session
from backend.core.exceptions import TagNotFoundError
from backend.schemas.tags import (
    TagCreateDTO,
    TagListQueryDTO,
    TagResponseDTO,
    TagUpdateDTO,
)
from backend.services.tag_service import TagService

tags_bp = Blueprint("tags", __name__, url_prefix="/tags")


@tags_bp.get("")
def get_tags():
    query_params = TagListQueryDTO.model_validate(request.args.to_dict())

    with get_db_session() as session:
        service = TagService(session)
        tags = service.get_list(query_params.limit, query_params.offset)

        return jsonify([
            TagResponseDTO.model_validate(tag).model_dump(mode="json") for tag in tags
        ])


@tags_bp.post("")
def create_tag():
    tag_dto = TagCreateDTO.model_validate(request.get_json(silent=True) or {})

    with get_db_session() as session:
        service = TagService(session)
        tag = service.create_tag(tag_dto.name)
        response_dto = TagResponseDTO.model_validate(tag)

        return jsonify(response_dto.model_dump(mode="json")), 201


@tags_bp.get("/<int:tag_id>")
def get_tag(tag_id: int):
    with get_db_session() as session:
        service = TagService(session)
        try:
            tag = service.get_by_id(tag_id)
            response_dto = TagResponseDTO.model_validate(tag)
        except TagNotFoundError:
            return jsonify({"error": "Tag not found"}), 404

        return jsonify(response_dto.model_dump(mode="json")), 200


@tags_bp.patch("/<int:tag_id>")
def update_tag(tag_id: int):
    tag_dto = TagUpdateDTO.model_validate(request.get_json(silent=True) or {})

    with get_db_session() as session:
        service = TagService(session)
        try:
            updated_tag = service.update_tag(tag_id, tag_dto.name)
            response_dto = TagResponseDTO.model_validate(updated_tag)
        except TagNotFoundError:
            return jsonify({"error": "Tag not found"}), 404

        return jsonify(response_dto.model_dump(mode='json'))


@tags_bp.delete("/<int:tag_id>")
def delete_tag(tag_id: int):
    with get_db_session() as session:
        service = TagService(session)
        try:
            service.delete_tag(tag_id)
        except TagNotFoundError:
            return jsonify({"error": "Tag not found"}), 404

        return jsonify({"success": "Tag deleted successfully"}), 200
