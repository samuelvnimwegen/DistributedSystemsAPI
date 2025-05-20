"""
This keeps track of the watched movies for each user.
"""

from datetime import datetime
from flask_restx import Namespace, Resource, fields, Api, marshal
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.database import db
from src.database.models.watched_movie import WatchedMovie

watched_movie_api = Namespace("watched", description="Watched movie related operations")

watched_movie_parser = watched_movie_api.parser()
watched_movie_parser.add_argument(
    "watched_at", type=str, required=False, help="The date and time when the movie was watched."
)

watched_movie_model = watched_movie_api.model(
    "WatchedMovie",
    {
        "movie_id": fields.Integer(required=True, description="The ID of the movie that was watched."),
        "user_id": fields.Integer(required=True, description="The ID of the user who watched the movie."),
        "watched_at": fields.DateTime(
            required=True, description="The date and time when the movie was watched."
        ),
    },
)

watched_movie_list_model = watched_movie_api.model(
    "WatchedMovieList",
    {
        "results": fields.List(fields.Nested(watched_movie_model), description="List of watched movies"),
    },
)

watched_users_parser = watched_movie_api.parser()
watched_users_parser.add_argument(
    "user_id", type=int, required=False, help="The ID of the user to get watched movies for.", action="append"
)
watched_users_parser.add_argument(
    "movie_id", type=int, required=False, help="The ID of the movie to get watched movies for.", action="append"
)
watched_users_parser.add_argument(
    "since_timestamp", type=str, required=False, help="The timestamp to filter watched movies since."
)


@watched_movie_api.route("/<int:movie_id>")
class WatchedMovieResource(Resource):
    """
    Resource for managing watched movies.
    """

    @watched_movie_api.response(200, "Success")
    @watched_movie_api.response(400, "Bad Request")
    @watched_movie_api.response(401, "Unauthorized")
    @jwt_required()
    def post(self, movie_id):
        """
        Mark a movie as watched by the user.
        """
        user_id = int(get_jwt_identity())

        watched_movie = WatchedMovie(
            user_id=user_id,
            movie_id=movie_id,
        )

        # Save the watched movie to the database
        db.session.add(watched_movie)
        db.session.commit()

        return {"message": "Movie marked as watched"}, 200

    @watched_movie_api.doc(params={"movie_id": "The ID of the movie to check if it's watched."})
    @watched_movie_api.response(200, "Success")
    @jwt_required()
    def get(self, movie_id):
        """
        Get the watched status of a movie. This is whether the movie is in the watched list or not.
        """
        user_id = int(get_jwt_identity())
        if db.session.query(WatchedMovie).filter_by(user_id=user_id, movie_id=movie_id).first():
            return {"message": "Movie is watched."}
        return {"message": "Movie is not in the watched list."}


@watched_movie_api.route("")
class WatchedMoviesResource(Resource):
    """
    Resource for managing watched movies.
    """

    @watched_movie_api.expect(watched_users_parser)
    @watched_movie_api.response(200, "Success", model=watched_movie_list_model)
    @watched_movie_api.response(400, "Bad Request")
    @watched_movie_api.response(401, "Unauthorized")
    @jwt_required()
    def get(self):
        """
        Get a list of all watched movies for the requested users since the given timestamp.
        """
        data = watched_users_parser.parse_args()
        watched_movies = db.session.query(WatchedMovie)
        if data.get("user_id", None):
            watched_movies = watched_movies.filter(WatchedMovie.user_id.in_(data["user_id"]))
        if data.get("movie_id", None):
            watched_movies = watched_movies.filter(WatchedMovie.movie_id.in_(data["movie_id"]))
        if data.get("since_timestamp", None):
            watched_movies = watched_movies.filter(
                WatchedMovie.watched_at >= datetime.fromisoformat(data["since_timestamp"])
            )
        watched_movies = watched_movies.all()
        return marshal({"results": watched_movies}, watched_movie_list_model), 200


def register_routes(api_blueprint: Api) -> None:
    """
    Register the movies API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(watched_movie_api)
