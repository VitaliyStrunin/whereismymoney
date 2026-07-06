from flask import Blueprint, jsonify
from flask_pydantic import validate

from backend.api.dependencies import get_current_user_id, get_db_session
from backend.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from backend.schemas.user import (
    TokenResponseDTO,
    UserCreateDTO,
    UserLoginDTO,
    UserResponseDTO,
)
from backend.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/register")
@validate()
def register_user(body: UserCreateDTO):
    with get_db_session() as session:
        service = AuthService(session)

        try:
            user = service.register(body.email, body.plain_password)
            response_dto = UserResponseDTO.model_validate(user)
        except UserAlreadyExistsError:
            return jsonify({"error": "User already exists"}), 409

        return jsonify(response_dto.model_dump(mode="json")), 201


@auth_bp.post("/login")
@validate()
def login(login_data: UserLoginDTO):
    with get_db_session() as session:
        service = AuthService(session)

        try:
            access_token = service.login(login_data.email, login_data.plain_password)
            response_dto = TokenResponseDTO(access_token=access_token)
        except InvalidCredentialsError:
            return jsonify({"error": "Wrong login or password"}), 401

        return jsonify(response_dto.model_dump(mode="json")), 200


@auth_bp.get("/me")
def get_me():
    current_user_id = get_current_user_id()

    with get_db_session() as session:
        service = AuthService(session)

        try:
            user = service.get_user_by_id(current_user_id)
            response_dto = UserResponseDTO.model_validate(user)
        except UserNotFoundError:
            return jsonify({"error": "User not found"}), 404

        return jsonify(response_dto.model_dump(mode="json")), 200

