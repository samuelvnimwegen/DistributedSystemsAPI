"""
This module is the entry point of the application.
It sets up the Flask app with the given configuration
from the environment variables (in .env file or in the system).
"""
import logging
import os

from confz import EnvSource
from flask import Flask
from flask_cors import CORS
from src.config import APIConfig
from src.database.database import db
from src.routes import register_public_routes
# from src.routes.error_handlers import register_error_handlers


def create_app(api_config: APIConfig) -> Flask:
    """
    Set up the Flask app with the given configuration from the environment variables
    (in .env file or in the system)
    :param api_config: The configuration to use
    """
    logging.basicConfig(level=api_config.logging.get_level(),
                        format=api_config.logging.format, filename=api_config.logging.file)

    logging.info("Setting up %s", api_config.name)

    flask_app = Flask(api_config.name, instance_path=os.getcwd())

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = api_config.db.connection_url
    flask_app.config["SECRET_KEY"] = api_config.secret_key
    flask_app.config["DEBUG"] = api_config.debug

    CORS(flask_app)

    db.init_app(flask_app)

    # Register the error handlers and public routes
    # if not api_config.debug:
    #     register_error_handlers(flask_app)

    register_public_routes(flask_app)

    logging.info("App %s has been setup", flask_app.name)
    return flask_app


if __name__ == '__main__':
    config = APIConfig(config_sources=EnvSource(allow_all=True, nested_separator="__", file=".env"))
    app = create_app(config)
    app.run(host=config.host, port=config.port)
