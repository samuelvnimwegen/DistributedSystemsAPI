"""
This module contains the database access class that contains all the access methods
"""
import os
import requests
from flask_restx import Namespace, Api, Resource, fields

TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")

movies_api = Namespace("movies", description="Movie Operations")

get_popular_parser = movies_api.parser()
get_popular_parser.add_argument(
    "amount",
    type=int,
    default=1,
    help="Number of popular movies to fetch, minimum 1, maximum 20",
)

movie_model = movies_api.model(
    "Movie",
    {
        "id": fields.Integer(description="Movie ID"),
        "title": fields.String(description="Movie title"),
        "overview": fields.String(description="Movie overview"),
        "original_language": fields.String(description="Original language"),
        "original_title": fields.String(description="Original title"),
        "release_date": fields.String(description="Release date"),
        "poster_path": fields.String(description="Poster path"),
        "popularity": fields.Float(description="Popularity score"),
        "vote_average": fields.Float(description="Vote average"),
        "vote_count": fields.Integer(description="Vote count"),
        "backdrop_path": fields.String(description="Backdrop path"),
        "adult": fields.Boolean(description="Is adult content"),
        "genre_ids": fields.List(fields.Integer, description="List of genre IDs"),
    },
)

movie_list_model = movies_api.model(
    "MovieList",
    {
        "results": fields.List(fields.Nested(movie_model), description="List of movies"),
    }
)


@movies_api.route('/popular', methods=['GET'])
class PopularMoviesResource(Resource):
    @movies_api.expect(get_popular_parser)
    @movies_api.marshal_with(movie_list_model)
    def get(self):
        """
        Get a list of popular movies.

        Returns a list of popular movies from the TMDB API.
        """
        args = get_popular_parser.parse_args()
        amount = args.get("amount", 1)

        if amount > 20:
            movies_api.abort(400, f"Maximum amount allowed amount is {20}.")
        if amount < 1:
            movies_api.abort(400, f"Minimum amount allowed amount is {1}.")

        headers = {
            "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}",
            "Accept": "application/json"
        }
        params = {
            "sort_by": "popularity.desc"
        }

        response = requests.get(
            "https://api.themoviedb.org/3/discover/movie",
            headers=headers,
            params=params,
            timeout=10,
        )

        if response.status_code != 200:
            movies_api.abort(response.status_code, "Failed to fetch data from TMDb.")

        movies = response.json().get("results", [])[:amount]

        return {"results": movies}


def register_routes(api_blueprint: Api) -> None:
    """
    Register the movies API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(movies_api)
