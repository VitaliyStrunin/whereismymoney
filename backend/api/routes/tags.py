from flask import Blueprint, jsonify, request

from backend.core.exceptions import TagNotFoundError
from backend.database.session import session_maker
from backend.models.tag import Tag
from backend.services.tag_service import TagService

tags_bp = Blueprint("tags", __name__, url_prefix="/tags")


def tag_to_dict(tag: Tag) -> dict:
    return {"id": tag.id, "name": tag.name}


@tags_bp.get("")
def get_tags():
    limit = request.args.get("limit", 100, type=int)
    offset = request.args.get("offset", 0, type=int)

    with session_maker() as session:
        service = TagService(session)
        tags = service.get_list(limit, offset)

    return jsonify([
        tag_to_dict(tag) for tag in tags
    ])


@tags_bp.post("")
def create_tag():
    data = request.get_json(silent=True) or {}
    name = data.get("name")

    if not name:
        return jsonify({"error": "name is required"}), 400

    with session_maker() as session:
        service = TagService(session)
        tag = service.create_tag(name)

    return jsonify(tag_to_dict(tag)), 201


@tags_bp.get("/<int:tag_id>")
def get_tag(tag_id: int):
    with session_maker() as session:
        service = TagService(session)
        try:
            tag = service.get_by_id(tag_id)
        except TagNotFoundError:
            return jsonify({"error": "Tag not found"}), 404

    return jsonify(tag_to_dict(tag)), 200


@tags_bp.patch("/<int:tag_id>")
def update_tag(tag_id: int):
    data = request.get_json(silent=True) or {}
    name = data.get("name")

    if name is None:
        return jsonify({"error": "name is required"}), 400

    with session_maker() as session:
        service = TagService(session)
        try:
            updated_tag = service.update_tag(tag_id, name)
        except TagNotFoundError:
            return jsonify({"error": "Tag not found"}), 404

    return jsonify(tag_to_dict(updated_tag))


@tags_bp.delete("/<int:tag_id>")
def delete_tag(tag_id: int):
    with session_maker() as session:
        service = TagService(session)
        try:
            service.delete_tag(tag_id)
        except TagNotFoundError:
            return jsonify({"error": "Tag not found"}), 404

    return jsonify({"success": "Tag deleted successfully"}), 200
