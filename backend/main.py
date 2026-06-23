from flask import Flask

from backend.api.routes.categories import categories_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(categories_bp)
    return app
