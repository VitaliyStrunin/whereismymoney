from flask import Flask, jsonify
from pydantic import ValidationError

from backend.api.routes.auth import auth_bp
from backend.api.routes.categories import categories_bp
from backend.api.routes.expenses import expenses_bp
from backend.api.routes.tags import tags_bp
from backend.core.exceptions import AccessTokenExpiredError, InvalidAccessTokenError, InvalidRefreshTokenError
from backend.database.session import session_maker


def create_app(config: dict | None = None, session_factory=None) -> Flask:
    app = Flask(__name__)

    if config is not None:
        app.config.update(config)

    app.extensions["session_factory"] = session_factory or session_maker

    app.register_blueprint(categories_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(auth_bp)

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        return jsonify({"error": error.errors(include_context=False)}), 400

    @app.errorhandler(AccessTokenExpiredError)
    def handle_access_token_expired(error: AccessTokenExpiredError):
        response = jsonify({"error": "Access token expired"})
        response.status_code = 401
        response.headers["WWW-Authenticate"] = 'Bearer error="invalid_token"'
        return response

    @app.errorhandler(InvalidAccessTokenError)
    def handle_invalid_access_token(error: InvalidAccessTokenError):
        response = jsonify({"error": "Invalid or missing access token"})
        response.status_code = 401
        response.headers["WWW-Authenticate"] = 'Bearer error="invalid_token"'
        return response

    @app.errorhandler(InvalidRefreshTokenError)
    def handle_invalid_refresh_token(error:InvalidRefreshTokenError):
        response = jsonify({"error": "Invalid or expired refresh token"})
        response.status_code = 401
        response.headers["WWW-Authenticate"] = 'Bearer error="invalid_token"'
        return response

    return app
