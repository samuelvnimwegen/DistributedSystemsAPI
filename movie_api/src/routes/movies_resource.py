"""
This module contains the database access class that contains all the access methods
"""
import io
import json
import logging

import requests
from flask import send_file
from flask_restx import Namespace, Api, Resource, fields, marshal
from flask_jwt_extended import jwt_required, get_current_user
from src.routes.quickchart import QuickChartDataItem, create_quickchart_config
from src.database import db, Movie, Genre
from src.cache import cache
from src.limiter import limiter

# pylint: disable=no-member


movies_api = Namespace("", description="Movie Operations")

get_popular_parser = movies_api.parser()
get_popular_parser.add_argument(
    "amount",
    type=int,
    default=1,
    help="Number of popular movies to fetch, minimum 1, maximum 20",
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
        "plot": fields.String(description="Movie plot", attribute="description"),
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


@movies_api.route('', methods=['GET'])
class PopularMoviesResource(Resource):
    @movies_api.expect(get_popular_parser)
    @cache.cached(query_string=True)
    @limiter.limit("500 per hour")
    @limiter.limit("1000 per day")
    @limiter.limit("10000 per month")
    def get(self):
        """
        Get a list of movies.
        """
        args = get_popular_parser.parse_args()
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
        movie: Movie = db.session.query(Movie).filter_by(id=movie_id).first()
        return marshal(movie, movie_model)


@movies_api.route('/<int:movie_id>/same_genres', methods=['GET'])
@movies_api.doc(params={"movie_id": "The ID of the movie to get movies with the same genres for."})
class SameGenresResource(Resource):
    """
    Resource for fetching movies with the same genres as a given movie.
    """

    @movies_api.response(200, "Success", model=movie_list_model)
    @jwt_required()
    @cache.cached()
    def get(self, movie_id):
        """
        Get a list of movies with the same genres.

        Returns a list of movies with the same genres from the TMDB API.
        """
        movie: Movie = db.session.query(Movie).filter_by(id=movie_id).first()
        if not movie:
            movies_api.abort(404, "Movie not found.")

        genres: list[Genre] = movie.genres
        movies: list[Movie] = db.session.query(Movie).all()
        filtered_movies = [
            m for m in movies if all(g in m.genres for g in genres) and m.movie_id != movie_id
        ]

        return marshal({"results": filtered_movies}, movie_list_model)


@movies_api.route('/<int:movie_id>/similar_runtime', methods=['GET'])
@movies_api.doc(params={"movie_id": "The ID of the movie to get movies with a similar runtime for."})
class SimilarRuntimeResource(Resource):
    """
    Resource for fetching movies with the same runtime as a given movie (+- 10 minutes).
    """

    @movies_api.response(200, "Success", model=movie_list_model)
    @jwt_required()
    @cache.cached()
    def get(self, movie_id):
        """
        Get a list of movies with the same runtime (+- 10 minutes)
        """
        movie: Movie = db.session.query(Movie).filter_by(id=movie_id).first()
        if not movie:
            movies_api.abort(404, "Movie not found.")
        run_time: int = movie.runtime

        # Get movies with a similar runtime
        movies: list[Movie] = db.session.query(Movie).filter(
            Movie.runtime.between(run_time - 10, run_time + 10),
            Movie.movie_id != movie_id
        ).all()
        return movies


@movies_api.route('/score-plot', methods=['GET'])
class ScorePlotResource(Resource):
    """
    Resource for fetching a score plot for a set of movies.
    """

    @movies_api.expect(score_plot_parser)
    @jwt_required()
    @cache.cached(query_string=True)
    def get(self):
        """
        Get a score plot for a set of movies.
        """
        # Parse the movie IDs from the request arguments
        movie_ids: list[int] = score_plot_parser.parse_args().get("movie_ids", [])
        if not movie_ids:
            movies_api.abort(400, "No movie IDs provided.")

        # Get the ratings for the movies
        results: list[QuickChartDataItem] = []
        for movie_id in movie_ids:
            movie = db.session.query(Movie).filter_by(movie_id=movie_id).first()
            if not movie:
                movies_api.abort(404, f"Movie with ID {movie_id} not found.")

            results.append(QuickChartDataItem(
                title=movie.movie_name,
                rating=movie.rating,
            ))

        # Generate the quickchart configuration
        chart_config = create_quickchart_config(results)

        # Send the quickchart request
        quickchart_url = "https://quickchart.io/chart"
        response = requests.get(
            quickchart_url,
            params={"c": json.dumps(chart_config)},
            timeout=10,
        )
        logging.info("QuickChart response: %s", response.status_code)

        if response.status_code != 200:
            movies_api.abort(
                response.status_code, f"Failed to fetch data from QuickChart. Original error: {response.text}"
            )

        # Return the URL of the generated chart
        return send_file(
            io.BytesIO(response.content),
            mimetype="image/png",
            as_attachment=False,
            download_name="chart.png",
        )


def register_routes(api_blueprint: Api) -> None:
    """
    Register the movies API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(movies_api)
