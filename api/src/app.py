"""
This module is the entry point of the application.
It sets up the Flask app with the given configuration
from the environment variables (in .env file or in the system).

Disclaimer: This is based on our bachelor eindwerk project setup, which I also largely contributed to.
"""
import logging
import os
from datetime import timedelta
from dotenv import load_dotenv
from confz import EnvSource
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from src.config import APIConfig
from src.database.database import db
from src.routes import register_public_routes
from src.cache import cache
from src.limiter import limiter
from src.authentication import add_user_identity_lookup, add_user_lookup_callback, add_cookie_refresher
from src.error_handlers import register_error_handlers

load_dotenv()


def create_app(api_config: APIConfig) -> Flask:
    """
    Set up the Flask app with the given configuration from the environment variables
    (in .env file or in the system)

    Disclaimer: This is a commonly used setup for Flask applications, it could be used in other projects as well.
    :param api_config: The configuration to use
    """
    assert os.getenv("API_KEY") is not None, "API_KEY not loaded correctly"
    logging.basicConfig(
        level=api_config.logging.get_level(),
        format=api_config.logging.format,
        filename=api_config.logging.file
    )

    flask_app = Flask(api_config.name, instance_path=os.getcwd())

    flask_app.config["JWT_SECRET_KEY"] = api_config.secret_key
    flask_app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    flask_app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    flask_app.config["JWT_COOKIE_SECURE"] = False
    flask_app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
    flask_app.config['JWT_COOKIE_CSRF_PROTECT'] = True  # or False if you're testing without CSRF
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = api_config.db.connection_url
    flask_app.config["SECRET_KEY"] = api_config.secret_key
    flask_app.config["DEBUG"] = api_config.debug

    CORS(flask_app, supports_credentials=True)
    db.init_app(flask_app)
    cache.init_app(flask_app)
    limiter.init_app(flask_app)

    # Initialize JWT Manager
    jwt = JWTManager(flask_app)

    # Set up user identity and lookup callbacks right after JWTManager initialization
    add_user_identity_lookup(jwt)
    add_user_lookup_callback(jwt)

    # Register error handlers (routes could trigger these)
    register_error_handlers(jwt, flask_app)

    # Register routes
    register_public_routes(flask_app)

    # Cookie refresher logic
    add_cookie_refresher(flask_app)

    return flask_app


if __name__ == '__main__':
    config = APIConfig(config_sources=EnvSource(allow_all=True, nested_separator="__", file=".env"))
    app = create_app(config)
    app.run(host=config.host, port=config.port)
