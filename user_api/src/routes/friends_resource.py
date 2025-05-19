"""
This module contains the friend resource for the application.
"""

from flask_restx import Namespace, Api, Resource, fields, marshal
from flask_jwt_extended import jwt_required, get_current_user
from src.database.models import User
from src.database import db

friends_ns = Namespace("friends", description="Friends operations")

friend_model = friends_ns.model(
    "Friend",
    {
        "username": fields.String(description="Username of the friend"),
        "user_id": fields.Integer(description="User ID of the friend"),
    },
)
friends_list_model = friends_ns.model(
    "FriendsList",
    {
        "results": fields.List(fields.Nested(friend_model), description="List of friends"),
    },
)

friend_parser = friends_ns.parser()
friend_parser.add_argument(
    "username", type=str, required=True, help="Username of the friend to add", location="json",
)


@friends_ns.route("")
class FriendsResource(Resource):
    """
    This resource contains a GET method for fetching the friends the current user has.
    """

    @friends_ns.response(200, "Success")
    @friends_ns.response(401, "Unauthorized")
    @jwt_required()
    def get(self):
        """
        Get the friends of the current user.
        """
        user = get_current_user()

        friends: list[User] = user.get_friends()
        return marshal({"results": friends}, friends_list_model), 200

    @friends_ns.expect(friend_parser)
    @friends_ns.response(200, "Success")
    @friends_ns.response(401, "Unauthorized")
    @friends_ns.response(404, "User not found")
    @jwt_required()
    def post(self):
        """
        Add a friend to the current user.
        """
        args = friend_parser.parse_args()
        username = args["username"]

        user = get_current_user()
        friend = db.session.query(User).filter_by(username=username).first()

        if not friend:
            return {"message": f"User with username '{username}' not found"}, 404

        user.add_friend(friend)
        db.session.commit()

        return {"message": "Friend added successfully"}, 200


def register_routes(api_blueprint: Api) -> None:
    """
    Register the login API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(friends_ns)
