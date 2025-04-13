"""
This module defines the logout resource for the API.
"""

from flask import jsonify
from flask_restx import Namespace, Api, Resource
from flask_jwt_extended import unset_jwt_cookies

# Define the logout API namespace
logout_api = Namespace("logout", description="Logout operations")


@logout_api.route("", methods=["POST"])
class LogoutResource(Resource):
    """
    This resource handles the logout functionality.
    """

    @logout_api.response(200, "Logout successful")
    def post(self):
        """
        Handle the logout request.
        """
        response = jsonify({"msg": "Logout successful"})
        unset_jwt_cookies(response)
        return response


def register_routes(api_blueprint: Api) -> None:
    """
    Register the logout API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(logout_api)
