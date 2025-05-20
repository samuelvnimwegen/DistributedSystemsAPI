"""
This module contains the user resource API for managing user-related operations.
"""

from flask import jsonify
from flask_restx import Namespace, Resource, fields, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database.models import User
from src.database import db

user_ns = Namespace("retrieve", description="User operations")

user_model = user_ns.model(
    "User",
    {
        "username": fields.String(description="Username of the user"),
        "user_id": fields.Integer(description="User ID of the user"),
    },
)
user_list_model = user_ns.model(
    "UserList",
    {
        "results": fields.List(fields.Nested(user_model), description="List of users"),
    },
)


def str2bool(value):
    """
    Convert a string to a boolean value.
    """
    if value.lower() in ("true", "1"):
        return True
    if value.lower() in ("false", "0"):
        return False
    raise ValueError("Invalid boolean value")


user_list_parser = user_ns.parser()
user_list_parser.add_argument(
    "self_included", type=str2bool, required=False, help="Include the current user in the list.", default=False
)


@user_ns.route("/<int:user_id>")
class UserResource(Resource):
    """
    This resource contains a GET method for fetching the user with the given ID.
    """

    @user_ns.response(200, "Success", user_model)
    @user_ns.response(401, "Unauthorized")
    @jwt_required()
    def get(self, user_id):
        """
        Get the user with the given ID.
        """
        user = db.session.query(User).filter(User.user_id == user_id).first()
        if not user:
            return {"message": "User not found"}, 404
        return jsonify({"username": user.username, "user_id": user.user_id})


@user_ns.route("/<string:username>")
class UserResourceByName(Resource):
    """
    This resource contains a GET method for fetching the user with the given username.
    """

    @user_ns.response(200, "Success", user_model)
    @user_ns.response(401, "Unauthorized")
    @jwt_required()
    def get(self, username):
        """
        Get the user with the given username.
        """
        user = db.session.query(User).filter_by(username=username).first()
        if not user:
            return {"message": "User not found"}, 404
        return jsonify({"username": user.username, "user_id": user.user_id})


@user_ns.route("")
class UsersResource(Resource):
    """
    This resource contains a GET method for fetching all users except the current user.
    """
    @user_ns.expect(user_list_parser)
    @user_ns.response(200, "Success", user_list_model)
    @user_ns.response(401, "Unauthorized")
    @jwt_required()
    def get(self):
        """
        Get all users (including the current user if specified).
        """
        args = user_list_parser.parse_args()
        self_included = args.get("self_included", False)

        user_id = int(get_jwt_identity())
        if not self_included:
            users = db.session.query(User).filter(User.user_id != user_id).all()
        else:
            users = db.session.query(User).all()
        return jsonify({"results": [{"username": user.username, "user_id": user.user_id} for user in users]})


def register_routes(api_blueprint: Api) -> None:
    """
    Register the login API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(user_ns)
