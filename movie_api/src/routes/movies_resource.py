"""
This module contains the database access class that contains all the access methods
"""
from flask_restx import Namespace, Api, Resource, fields, marshal
from src.database import db, Movie
from src.cache import cache
from src.limiter import limiter

# pylint: disable=no-member


movies_api = Namespace("", description="Movie Operations")

get_movies_parser = movies_api.parser()
get_movies_parser.add_argument(
    "amount",
    type=int,
    default=1,
    help="Number of popular movies to fetch, minimum 1, maximum 20",
)
get_movies_parser.add_argument(
    "movie_ids", type=int, action="append", help="List of movie ids to fetch", required=False
)

genre_model = movies_api.model(
    "Genre",
    {
        "genre_id": fields.Integer(description="Genre ID"),
        "genre_name": fields.String(description="Genre name"),
    },
)

movie_model = movies_api.model(
    "Movie",
    {
        "movie_id": fields.Integer(description="Movie ID"),
        "movie_name": fields.String(description="Movie title"),
        "plot": fields.String(description="Movie plot"),
        "poster_path": fields.String(description="Poster path", attribute=lambda m: m.get_poster_path()),
        "rating": fields.Float(description="Vote average"),
        "genres": fields.List(fields.Nested(genre_model), description="List of genres"),
        "meta_score": fields.Integer(description="Meta score"),
        "runtime": fields.Integer(description="Runtime in minutes"),
    },
)

movie_list_model = movies_api.model(
    "MovieList",
    {
        "results": fields.List(fields.Nested(movie_model), description="List of movies"),
    }
)

score_plot_parser = movies_api.parser()
score_plot_parser.add_argument(
    "movie_ids",
    type=int,
    action="split",
    required=True,
    help="List of movie IDs to fetch scores for",
)

is_favorite_model = movies_api.model(
    "IsFavorite",
    {
        "is_favorite": fields.Boolean(description="Is the movie a favorite"),
    },
)


@movies_api.route('/list', methods=['GET'])
class PopularMoviesResource(Resource):
    @movies_api.expect(get_movies_parser)
    @cache.cached(query_string=True)
    @limiter.limit("500 per hour")
    @limiter.limit("1000 per day")
    @limiter.limit("10000 per month")
    @movies_api.response(200, "Success", model=movie_list_model)
    def get(self):
        """
        Get a list of movies automatically sorted by rating.
        """
        args = get_movies_parser.parse_args()
        if args.get("movie_ids", None):
            movie_ids = args.get("movie_ids")
            movie_list = db.session.query(Movie).filter(Movie.movie_id.in_(movie_ids)).all()
            if not movie_list:
                movies_api.abort(404, "Movies not found.")
            return marshal({"results": movie_list}, movie_list_model)

        amount = args.get("amount", 1)

        movie_list = db.session.query(Movie).all()[:amount]

        return marshal({"results": movie_list}, movie_list_model)


@movies_api.route('/<int:movie_id>', methods=['GET'])
class MovieResource(Resource):
    """
    Resource for fetching movie details.
    """

    @movies_api.response(200, "Success", model=movie_model)
    @movies_api.response(404, "Movie not found")
    @movies_api.doc(params={"movie_id": "The ID of the movie to fetch."})
    @cache.cached()
    def get(self, movie_id):
        """
        Get movie details by ID.

        Returns the details of a movie from the TMDB API.
        """
        movie: Movie = db.session.query(Movie).filter(Movie.movie_id == movie_id).first()
        return marshal(movie, movie_model)


def register_routes(api_blueprint: Api) -> None:
    """
    Register the movies API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(movies_api)
