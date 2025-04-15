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
from flask_jwt_extended import jwt_required
from src.routes.quickchart import QuickChartDataItem, create_quickchart_config
from src.cache import cache
from src.limiter import limiter

API_KEY = os.getenv("API_KEY")
TMDB_ACCOUNT_ID = os.getenv("TMDB_ACCOUNT_ID")

API_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
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

is_favorite_model = movies_api.model(
    "IsFavorite",
    {
        "is_favorite": fields.Boolean(description="Is the movie a favorite"),
    },
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


@movies_api.route('', methods=['GET'])
class PopularMoviesResource(Resource):
    @movies_api.expect(get_popular_parser)
    @movies_api.marshal_with(movie_list_model)
    @cache.cached(query_string=True)
    @limiter.limit("500 per hour")
    @limiter.limit("1000 per day")
    @limiter.limit("10000 per month")
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
            "Authorization": f"Bearer {API_KEY}",
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


@movies_api.route('/<int:movie_id>', methods=['GET'])
class MovieResource(Resource):
    """
    Resource for fetching movie details.
    """

    @movies_api.doc(params={"movie_id": "The ID of the movie to fetch."})
    @movies_api.marshal_with(movie_model)
    @cache.cached()
    def get(self, movie_id):
        """
        Get movie details by ID.

        Returns the details of a movie from the TMDB API.
        """
        # Get the movie with the given ID
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            headers=API_HEADERS,
            timeout=10,
        )
        if response.status_code != 200:
            movies_api.abort(response.status_code, "Failed to fetch data from TMDb.")

        return response.json()


@movies_api.route('/<int:movie_id>/same_genres', methods=['GET'])
@movies_api.doc(params={"movie_id": "The ID of the movie to get movies with the same genres for."})
class SameGenresResource(Resource):
    """
    Resource for fetching movies with the same genres as a given movie.
    """

    @movies_api.marshal_with(movie_list_model)
    @jwt_required()
    @cache.cached()
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
    @jwt_required()
    @cache.cached()
    def get(self, movie_id):
        """
        Get a list of movies with the same runtime (+- 10 minutes)
        """
        headers = {
            "Authorization": f"Bearer {API_KEY}",
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


@movies_api.route('/favorite/<int:movie_id>')
class ChangeFavoriteResource(Resource):
    """
    Resource for changing the favorite status of a movie.
    """

    @jwt_required()
    def post(self, movie_id):
        """
        Add a movie to the favorite list.
        """
        # Get the request data
        data = {
            "media_type": "movie",
            "media_id": movie_id,
            "favorite": True,
        }

        # Send the request to the TMDb API
        response = requests.post(
            f"https://api.themoviedb.org/3/account/{TMDB_ACCOUNT_ID}/favorite",
            headers=API_HEADERS,
            json=data,
            timeout=10,
        )

        if response.status_code != 201:
            movies_api.abort(response.status_code, "Failed to fetch data from TMDb.")

        return {"message": "Movie added to favorites."}

    @jwt_required()
    def delete(self, movie_id):
        """
        Remove a movie from the favorite list.
        """
        # Get the request data
        data = {
            "media_type": "movie",
            "media_id": movie_id,
            "favorite": False,
        }

        # Send the request to the TMDb API
        response = requests.post(
            f"https://api.themoviedb.org/3/account/{TMDB_ACCOUNT_ID}/favorite",
            headers=API_HEADERS,
            json=data,
            timeout=10,
        )

        if response.status_code != 200:
            movies_api.abort(response.status_code, "Failed to fetch data from TMDb.")

        return {"message": "Movie removed from favorites."}

    @movies_api.doc(params={"movie_id": "The ID of the movie to check if it's a favorite."})
    @movies_api.marshal_with(is_favorite_model)
    @jwt_required()
    def get(self, movie_id):
        """
        Get the favorite status of a movie. This is whether the movie is in the favorite list or not.
        """
        # Send the request to the TMDb API
        response = requests.get(
            f"https://api.themoviedb.org/3/account/{TMDB_ACCOUNT_ID}/favorite/movies",
            headers=API_HEADERS,
            timeout=10,
        )

        if response.status_code != 200:
            movies_api.abort(response.status_code, "Failed to fetch data from TMDb.")

        # Check if the movie is in the favorite list
        movies = response.json().get("results", [])
        is_favorite = any(movie["id"] == movie_id for movie in movies)

        return {"is_favorite": is_favorite}


@movies_api.route('/favorite', methods=['GET'])
class GetFavoriteMoviesResource(Resource):
    """
    Resource for fetching the favorite movies of a user.
    """

    @movies_api.marshal_with(movie_list_model)
    @jwt_required()
    def get(self):
        """
        Get the favorite movies of a user.
        """
        # Send the request to the TMDb API
        response = requests.get(
            f"https://api.themoviedb.org/3/account/{TMDB_ACCOUNT_ID}/favorite/movies",
            headers=API_HEADERS,
            timeout=10,
        )

        if response.status_code != 200:
            movies_api.abort(response.status_code, "Failed to fetch data from TMDb.")

        return response.json()


def register_routes(api_blueprint: Api) -> None:
    """
    Register the movies API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(movies_api)
