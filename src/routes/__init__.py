"""
This module is responsible for dynamically importing all other routes in the
'routes' directory

Disclaimer: This is based on our bachelor eindwerk project setup, which I also largely contributed to.
"""
import importlib
import os

from flask import Blueprint
from flask_restx import Api
from flask_restx.apidoc import apidoc


def register_public_routes(app: Blueprint) -> None:
    """
    This function recurses through the 'routes' directory and registers all files with a
    'register_routes(api)' function
    :param app:
    """
    # Set the static URL path for the Swagger UI assets
    apidoc.static_url_path = "/api/swaggerui"

    # Create a Blueprint to register routes
    bp = Blueprint("DS_API", __name__, url_prefix="/api",
                   static_url_path='/api/swaggerui')
    api = Api(
        bp,
        version="1.0",
        title="",
        description="API documentation for the Distributed Systems project API",
        doc='/'
    )

    # Get the current package's directory
    package_dir = os.path.dirname(__file__)

    # Dynamically import all Python modules in the package
    for filename in os.listdir(package_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"{__name__}.{filename[:-3]}"  # Convert to module path
            # Dynamically load the module
            module = importlib.import_module(module_name)

            # If the module has a `register_routes` function, call it
            if hasattr(module, "register_routes"):
                module.register_routes(api)

    # Register the Blueprint with the Flask app
    # This must be the last step as registered blueprints cannot be modified afterwards
    app.register_blueprint(bp)
