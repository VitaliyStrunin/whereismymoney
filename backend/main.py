from flask import Flask, jsonify
from pydantic import ValidationError

from backend.api.routes.auth import auth_bp
from backend.api.routes.categories import categories_bp
from backend.api.routes.expenses import expenses_bp
from backend.api.routes.tags import tags_bp
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


    return app
