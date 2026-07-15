from flask import Blueprint, jsonify, request
from flask_pydantic import validate

from backend.api.dependencies import get_current_user_id, get_db_session
from backend.core.config import settings
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


def set_refresh_cookie(response, refresh_token: str):
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.REFRESH_TOKEN_SECURE,
        samesite=settings.REFRESH_TOKEN_SAMESITE,
        path="/auth"
    )


def clear_refresh_cookie(response):
    response.delete_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        path="/auth"
    )


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
def login(body: UserLoginDTO):
    with get_db_session() as session:
        service = AuthService(session)

        try:
            access_token, refresh_token = service.login(body.email, body.plain_password)
            response_dto = TokenResponseDTO(access_token=access_token)
        except InvalidCredentialsError:
            return jsonify({"error": "Wrong login or password"}), 401

        response = jsonify(response_dto.model_dump(mode="json"))
        set_refresh_cookie(response, refresh_token)
        return response, 200


@auth_bp.post("/refresh")
def refresh():
    raw_refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)

    with get_db_session() as session:
        service = AuthService(session)

        access_token, refresh_token = service.refresh(raw_refresh_token)
        response_dto = TokenResponseDTO(access_token=access_token)

        response = jsonify(response_dto.model_dump(mode="json"))
        set_refresh_cookie(response, refresh_token)

        return response, 200


@auth_bp.post("/logout")
def logout():
    raw_refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)

    with get_db_session() as session:
        service = AuthService(session)
        service.logout(raw_refresh_token)

        response = jsonify({"success": "Logged out successfully"})
        clear_refresh_cookie(response)
        return response, 200


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

