"""
This module contains the login route for the application.
"""
from flask import jsonify
from flask_restx import Namespace, Api, Resource
from flask_jwt_extended import create_access_token, set_access_cookies
from src.database.models import User
from src.database import db

login_api = Namespace("login", description="Login operations")

login_parser = login_api.parser()
login_parser.add_argument(
    "username", type=str, required=True, help="Username for login", location="json",
)
login_parser.add_argument(
    "password", type=str, required=True, help="Password for login", location="json",
)


@login_api.route("", methods=["POST"])
class LoginResource(Resource):
    """
    This resource handles the login functionality.
    """

    @login_api.expect(login_parser)
    @login_api.response(200, "Login successful")
    @login_api.response(401, "Invalid username or password")
    def post(self):
        """
        Handle the login request.
        """
        args = login_parser.parse_args()
        username = args["username"]
        password = args["password"]

        response = jsonify({"msg": "Login successful"})

        session = db.session
        user = session.query(User).filter_by(username=username).first()
        if not user or not user.check_password(password):
            return {"message": "Invalid username or password"}, 401

        access_token = create_access_token(identity=user)
        set_access_cookies(response, access_token)
        return response


def register_routes(api_blueprint: Api) -> None:
    """
    Register the login API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(login_api)
