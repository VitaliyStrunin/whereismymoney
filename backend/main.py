from flask import Flask

from backend.api.routes.categories import categories_bp
from backend.api.routes.tags import tags_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(categories_bp)
    app.register_blueprint(tags_bp)
    return app
