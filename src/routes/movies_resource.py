"""
This module contains the database access class that contains all the access methods
"""
import io
import json
import logging
import os
import requests
from flask import send_file
from flask_restx import Namespace, Api, Resource, fields
from src.routes.quickchart import QuickChartDataItem, create_quickchart_config

TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN")

API_HEADERS = {
    "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}",
    "Accept": "application/json"
}

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

score_plot_parser = movies_api.parser()
score_plot_parser.add_argument(
    "movie_ids",
    type=int,
    action="split",
    required=True,
    help="List of movie IDs to fetch scores for",
)


def query_movies(headers: dict[str, str | int], params: dict[str, str | int], original_movie_id: int):
    """
    Query the TMDb API for movies with the given parameters.
    :param headers: The headers to include in the request.
    :param params: The parameters to include in the request.
    :param original_movie_id: The ID of the original movie to exclude from the results.
    :return:
    """
    response = requests.get(
        "https://api.themoviedb.org/3/discover/movie",
        headers=headers,
        params=params,
        timeout=10,
    )
    if response.status_code != 200:
        movies_api.abort(response.status_code, "Failed to fetch data from TMDb.")
    movies = response.json().get("results", [])

    # Remove the movie that is queries
    movies = [movie for movie in movies if movie["id"] != original_movie_id]

    return {"results": movies}


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


@movies_api.route('/<int:movie_id>/same_genres', methods=['GET'])
@movies_api.doc(params={"movie_id": "The ID of the movie to get movies with the same genres for."})
class SameGenresResource(Resource):
    """
    Resource for fetching movies with the same genres as a given movie.
    """

    @movies_api.marshal_with(movie_list_model)
    def get(self, movie_id):
        """
        Get a list of movies with the same genres.

        Returns a list of movies with the same genres from the TMDB API.
        """
        # Get the movie with the given ID
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            headers=API_HEADERS,
            timeout=10,
        )
        if response.status_code != 200:
            movies_api.abort(response.status_code, "Failed to fetch data from TMDb.")

        genres = response.json().get("genres", [])
        genre_ids: list[int] = [genre["id"] for genre in genres]
        if not genre_ids:
            movies_api.abort(400, "No genres found for the given movie ID.")

        # Get movies with the same genres
        params = {
            "with_genres": ",".join(map(str, genre_ids)),
            "sort_by": "popularity.desc",
        }
        results = query_movies(API_HEADERS, params, movie_id)
        return results


@movies_api.route('/<int:movie_id>/similar_runtime', methods=['GET'])
@movies_api.doc(params={"movie_id": "The ID of the movie to get movies with a similar runtime for."})
class SimilarRuntimeResource(Resource):
    """
    Resource for fetching movies with the same runtime as a given movie (+- 10 minutes).
    """

    @movies_api.marshal_with(movie_list_model)
    def get(self, movie_id):
        """
        Get a list of movies with the same runtime (+- 10 minutes)
        """
        headers = {
            "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}",
            "Accept": "application/json"
        }

        # Get the movie with the given ID
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            headers=headers,
            timeout=10,
        )

        if response.status_code != 200:
            movies_api.abort(response.status_code, "Failed to fetch data from TMDb.")

        runtime = response.json().get("runtime", 0)
        logging.info("Runtime: %s", runtime)
        if runtime == 0:
            movies_api.abort(400, "No runtime found for the given movie ID.")

        # Get movies with the same runtime
        params = {
            "with_runtime.gte": runtime - 10,
            "with_runtime.lte": runtime + 10,
            "sort_by": "popularity.desc",
        }
        results = query_movies(headers, params, movie_id)
        return results


@movies_api.route('/score-plot', methods=['GET'])
class ScorePlotResource(Resource):
    """
    Resource for fetching a score plot for a set of movies.
    """

    @movies_api.expect(score_plot_parser)
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
            response = requests.get(
                f"https://api.themoviedb.org/3/movie/{movie_id}",
                headers=API_HEADERS,
                timeout=10,
            )
            if response.status_code != 200:
                movies_api.abort(response.status_code, "Failed to fetch data from TMDb.")
            results.append(QuickChartDataItem(
                title=response.json().get("original_title", ""),
                rating=response.json().get("vote_average", 0),
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
