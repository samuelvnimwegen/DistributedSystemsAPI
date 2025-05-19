"""
This module contains the resource for handling ratings and favorites.
"""
import requests
from flask import request
from flask_restx import Namespace, Resource, Api, fields, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.database import db, Rating

rating_ns = Namespace("rating", description="Rating operations")

rating_parser = rating_ns.parser()
rating_parser.add_argument(
    "rating", type=float, required=True, help="Rating value (1-10)"
)
rating_parser.add_argument(
    "review", type=str, required=False, help="Review text"
)

friend_rating_parser = rating_ns.parser()
friend_rating_parser.add_argument(
    "movie_id", type=int, required=False, help="Movie id"
)

rating_model = rating_ns.model(
    "Rating",
    {
        "rating_id": fields.Integer(description="Rating ID"),
        "rating": fields.Float(description="Rating value"),
        "review": fields.String(description="Review text"),
        "user_id": fields.Integer(description="User ID"),
        "movie_id": fields.Integer(description="Movie ID"),
    },
)

rating_list_model = rating_ns.model(
    "RatingList",
    {
        "results": fields.List(fields.Nested(rating_model), description="List of ratings"),
    },
)


@rating_ns.route("/<int:movie_id>")
class RatingResource(Resource):
    """
    Resource for handling ratings and favorites.
    """

    @rating_ns.expect(rating_parser)
    @rating_ns.response(200, "Success")
    @rating_ns.response(400, "Bad Request")
    @rating_ns.response(401, "Unauthorized")
    @rating_ns.response(404, "Not Found")
    @jwt_required()
    def post(self, movie_id):
        """
        Add a review to a movie.
        """
        user_id = int(get_jwt_identity())
        args = rating_parser.parse_args(request)

        # Check if the movie is watched
        jwt = request.cookies.get("access_token_cookie")
        response = requests.get(
            "http://logging_api:5001/api/logging/watched",
            params={"user_id": user_id, "movie_id": movie_id},
            cookies={"access_token_cookie": jwt},
            timeout=5,
        )
        if response.status_code != 200:
            return {"message": "error while getting watched movies", "error": response.json()}, 400
        if not response.json()["results"]:
            return {'message': "Movie not watched"}, 400

        # Make a rating
        rating = Rating(rating=args.get("rating"), review=args.get("review", ""), user_id=user_id, movie_id=movie_id)
        db.session.add(rating)
        db.session.commit()

        return {"message": f"Rating added successfully with id {rating.rating_id}"}, 200

    @rating_ns.response(200, "Success")
    @rating_ns.response(400, "Bad Request")
    @rating_ns.response(401, "Unauthorized")
    @rating_ns.response(404, "Not Found")
    @jwt_required()
    def delete(self, movie_id):
        """
        Delete a review from a movie.
        """
        user_id = int(get_jwt_identity())

        # Delete the rating
        rating = db.session.query(Rating).filter_by(user_id=user_id, movie_id=movie_id).first()
        if not rating:
            return {"message": "Rating does not exist"}, 404

        db.session.delete(rating)
        db.session.commit()

        return {"message": "Rating deleted successfully"}, 200


@rating_ns.route("/friends")
class FriendsResource(Resource):
    """
    Resource for fetching ratings from friends.
    """

    @rating_ns.expect(friend_rating_parser)
    @rating_ns.response(200, "Success", rating_list_model)
    @rating_ns.response(400, "Bad Request")
    @rating_ns.response(401, "Unauthorized")
    @rating_ns.response(404, "Not Found")
    @jwt_required()
    def get(self):
        """
        Get ratings from friends.
        """
        # Get the movie if it is provided
        args = friend_rating_parser.parse_args(request)
        movie_id = args.get("movie_id", None)

        # Ge the friends of the user
        response = requests.get(
            "http://user_api:5003/api/users/friends",
            cookies={"access_token_cookie": request.cookies.get("access_token_cookie")},
            timeout=5,
        )
        friends = response.json().get("results", [])
        friend_ids = [friend["user_id"] for friend in friends]

        # Get the movie ID from the request arguments
        query = db.session.query(Rating).filter(Rating.user_id.in_(friend_ids))
        if movie_id:
            query.filter(Rating.movie_id == movie_id)
        results: list[Rating] = query.all()

        return marshal({"results": results}, rating_list_model), 200


def register_routes(api_blueprint: Api) -> None:
    """
    Register the movies API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(rating_ns)
