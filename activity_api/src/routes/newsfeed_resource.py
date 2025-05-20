"""
This module contains the API endpoints for the newsfeed resource.
"""
import requests
from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Api, marshal, Resource

from src.database import db, WatchedMovie
from src.routes.watched_movie_resource import watched_movie_list_model

newsfeed_ns = Namespace("newsfeed", description="Newsfeed operations")


@newsfeed_ns.route("/")
class NewsfeedResource(Resource):
    """
    This resource handles the newsfeed operations.
    """
    @newsfeed_ns.response(200, "Success", model=watched_movie_list_model)
    @newsfeed_ns.response(401, "Unauthorized")
    @newsfeed_ns.response(404, "Not Found")
    @newsfeed_ns.response(500, "Internal Server Error")
    @jwt_required()
    def get(self):
        """
        Get the newsfeed data.
        """
        # Get the friends of the user
        response = requests.get(
            "http://user_api:5003/api/users/friends",
            cookies={"access_token_cookie": request.cookies.get("access_token_cookie")},
            timeout=5,
        )
        if response.status_code != 200:
            return {"message": f"Failed to fetch friends, error: {response.text}"}, response.status_code

        # Get the watched movies of the friends
        friends = response.json().get("results", [])
        if not friends:
            return {"results": []}, 200
        friend_ids = [friend["user_id"] for friend in friends]

        # Query the watched movies of the friends
        news_feed = db.session.query(WatchedMovie).filter(
            WatchedMovie.user_id.in_(friend_ids)
        ).order_by(WatchedMovie.watched_at.desc()).all()

        if not news_feed:
            return {"results": []}, 200

        # Return the watched movies of the friends
        return marshal({"results": news_feed}, watched_movie_list_model), 200


def register_routes(api_blueprint: Api) -> None:
    """
    Register the movies API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(newsfeed_ns)
