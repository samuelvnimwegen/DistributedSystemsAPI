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


@friends_ns.route("")
class FriendsResource(Resource):
    """
    This resource contains a GET method for fetching the friends the current user has.
    """

    @friends_ns.response(200, "Success", friends_list_model)
    @friends_ns.response(401, "Unauthorized")
    @jwt_required()
    def get(self):
        """
        Get the friends of the current user.
        """
        user = get_current_user()

        friends: list[User] = user.get_friends()
        return marshal({"results": friends}, friends_list_model), 200

    @friends_ns.route("/<string:user_name>")
    class FriendsAddResource(Resource):
        """
        This resource contains a POST method for adding a friend to the current user.
        """

        @friends_ns.response(200, "Success")
        @friends_ns.response(401, "Unauthorized")
        @friends_ns.response(404, "User not found")
        @jwt_required()
        def post(self, user_name):
            """
            Add a friend to the current user.
            """

            user = get_current_user()
            friend = db.session.query(User).filter_by(username=user_name).first()
            if user.username == user_name:
                return {"message": "You cannot add yourself as a friend."}, 400

            if not friend:
                return {"message": f"User with username '{user_name}' not found"}, 404

            user.add_friend(friend)
            db.session.commit()

            return {"message": "Friend added successfully"}, 200

        @friends_ns.response(200, "Success")
        @friends_ns.response(401, "Unauthorized")
        @friends_ns.response(404, "User not found")
        @jwt_required()
        def delete(self, user_name):
            """
            Remove a friend from the current user.
            """
            user = get_current_user()
            friend = db.session.query(User).filter_by(username=user_name).first()

            if not friend:
                return {"message": f"User with username '{user_name}' not found"}, 404

            if friend not in user.get_friends():
                return {"message": f"User with username '{user_name}' is not a friend"}, 400

            user.remove_friend(friend)
            db.session.commit()

            return {"message": "Friend removed successfully"}, 200


def register_routes(api_blueprint: Api) -> None:
    """
    Register the login API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(friends_ns)
