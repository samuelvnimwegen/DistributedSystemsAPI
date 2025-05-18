"""
This module defines the sign-up resource for the application.
"""

from flask import jsonify
from flask_restx import Namespace, Resource, Api
from flask_jwt_extended import create_access_token, set_access_cookies
from src.database.models import User
from src.database import db

# Define the sign-up API namespace
sign_up_api = Namespace("sign_up", description="Sign up operations")

# Define the sign-up request parser
sign_up_parser = sign_up_api.parser()
sign_up_parser.add_argument(
    "username", type=str, required=True, help="Username for sign up", location="json",
)
sign_up_parser.add_argument(
    "password", type=str, required=True, help="Password for sign up", location="json",
)


@sign_up_api.route("", methods=["POST"])
class SignUpResource(Resource):
    """
    This resource handles the sign-up functionality.
    """

    @sign_up_api.expect(sign_up_parser)
    @sign_up_api.response(201, "User created successfully")
    @sign_up_api.response(400, "Invalid input")
    def post(self):
        """
        Handle the sign-up request.
        """
        args = sign_up_parser.parse_args()
        username = args["username"]
        password = args["password"]

        # Check if the username already exists
        session = db.session()
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            return {"message": "Username already exists"}, 400

        # Check if username and password are valid
        if not username or not password:
            return {"message": "Username and password are required"}, 400
        if len(username) < 3:
            return {"message": "Username must be at least 3 characters long"}, 400
        if len(password) < 6:
            return {"message": "Password must be at least 6 characters long"}, 400

        # Create a new user
        new_user = User(username=username, password=password)
        session.add(new_user)
        session.commit()

        # Create a JWT access token for the new user
        access_token = create_access_token(identity=new_user)
        response = jsonify({"message": "User created successfully"})
        set_access_cookies(response, access_token)

        return response


def register_routes(api_blueprint: Api) -> None:
    """
    Register the sign-up API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(sign_up_api)
