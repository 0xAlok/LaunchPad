import os
import json

import yaml
from flask import Flask, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy import text

from .extensions import db, security, cache, mail
from .models import user_datastore

SWAGGER_URL = "/api/docs"
SPEC_URL = "/api/spec"


def _apply_sqlite_schema_patches():
    if db.engine.dialect.name != "sqlite":
        return

    app_columns = {
        row[1] for row in db.session.execute(text("PRAGMA table_info(application)")).fetchall()
    }
    if "company_feedback" not in app_columns:
        db.session.execute(text("ALTER TABLE application ADD COLUMN company_feedback TEXT"))
        db.session.commit()


def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('app.config')

    if config_name == "testing":
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
        app.config['CACHE_TYPE'] = "SimpleCache"

    required_secrets = ("SECRET_KEY", "SECURITY_PASSWORD_SALT")
    missing_secrets = [key for key in required_secrets if not app.config.get(key)]
    if app.config.get("REQUIRE_EXPLICIT_SECRETS") and missing_secrets:
        missing_list = ", ".join(missing_secrets)
        raise RuntimeError(f"Missing required configuration: {missing_list}")

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)

    db.init_app(app)
    CORS(app, supports_credentials=True)
    cache.init_app(app)
    mail.init_app(app)
    security.init_app(app, user_datastore)

    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.company import company_bp
    from .routes.student import student_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(company_bp, url_prefix="/api/company")
    app.register_blueprint(student_bp, url_prefix="/api/student")

    spec_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "api_docs.yaml")
    spec_path = os.path.normpath(spec_path)
    _spec_json = None

    @app.route(SPEC_URL)
    def serve_api_spec():
        nonlocal _spec_json
        if _spec_json is None:
            with open(spec_path) as f:
                _spec_json = json.dumps(yaml.safe_load(f))
        return app.response_class(_spec_json, mimetype="application/json")

    swagger_bp = get_swaggerui_blueprint(
        SWAGGER_URL,
        SPEC_URL,
        config={"app_name": "LaunchPad Placement Portal API"},
    )
    app.register_blueprint(swagger_bp, url_prefix=SWAGGER_URL)

    if config_name != "testing":
        from tasks import init_celery
        init_celery(app)

    with app.app_context():
        db.create_all()
        _apply_sqlite_schema_patches()

    return app
