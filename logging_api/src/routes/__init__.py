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
    apidoc.static_url_path = "/api/logging/swaggerui"

    # Create a Blueprint to register routes
    bp = Blueprint("LOGGING_API", __name__, url_prefix="/api/logging",
                   static_url_path='/api/logging/swaggerui')
    api = Api(
        bp,
        version="1.0",
        title="Logging Service API",
        description="API documentation for Logging Service of the Distributed Systems project",
        doc='/'
    )

    # Get the current package's directory
    package_dir = os.path.dirname(__file__)

    # Dynamically import all Python modules in the package
    for filename in os.listdir(package_dir):

        # Check if the file is a Python module and not the __init__.py file
        if filename.endswith(".py") and filename != "__init__.py":
            # If a module is found, construct the module name and import it dynamically
            module_name = f"{__name__}.{filename[:-3]}"
            module = importlib.import_module(module_name)

            # If the module has a `register_routes` function, call it to register the routes with the API
            if hasattr(module, "register_routes"):
                module.register_routes(api)

    # Register the Blueprint with the Flask app, this will make the routes available to the app
    app.register_blueprint(bp)
