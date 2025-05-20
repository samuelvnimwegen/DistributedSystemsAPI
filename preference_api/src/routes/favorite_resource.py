import requests
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, Api, fields

from src.database import db
from src.database.models.favorite_movie import FavoriteMovie

favorite_api = Namespace('favorite', description='Favorite movies related operations')

genre_model = favorite_api.model(
    "Genre",
    {
        "genre_id": fields.Integer(description="Genre ID"),
        "genre_name": fields.String(description="Genre name"),
    },
)

movie_model = favorite_api.model(
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

movie_list_model = favorite_api.model(
    "MovieList",
    {
        "results": fields.List(fields.Nested(movie_model), description="List of movies"),
    }
)


@favorite_api.route('/<int:movie_id>')
class ChangeFavoriteResource(Resource):
    """
    Resource for changing the favorite status of a movie.
    """

    @favorite_api.response(200, "Success")
    @jwt_required()
    def post(self, movie_id):
        """
        Add a movie to the favorite list.
        """
        user_id = int(get_jwt_identity())

        if db.session.query(FavoriteMovie).filter_by(user_id=user_id, movie_id=movie_id).first():
            return {"message": "Movie already in favorites."}

        db.session.add(FavoriteMovie(user_id=user_id, movie_id=movie_id))
        db.session.commit()

        return {"message": "Movie added to favorites."}

    @jwt_required()
    def delete(self, movie_id):
        """
        Remove a movie from the favorite list.
        """
        user_id = int(get_jwt_identity())
        favorite_movie = db.session.query(FavoriteMovie).filter_by(user_id=user_id, movie_id=movie_id).first()
        if not favorite_movie:
            return {"message": "Movie not in favorites."}
        db.session.delete(favorite_movie)
        db.session.commit()

        return {"message": "Movie removed from favorites."}

    @favorite_api.doc(params={"movie_id": "The ID of the movie to check if it's a favorite."})
    @favorite_api.response(200, "Success")
    @jwt_required()
    def get(self, movie_id):
        """
        Get the favorite status of a movie. This is whether the movie is in the favorite list or not.
        """
        user_id = int(get_jwt_identity())
        if db.session.query(FavoriteMovie).filter_by(user_id=user_id, movie_id=movie_id).first():
            return {"message": "Movie is a favorite."}
        return {"message": "Movie is not in the favorite list."}


@favorite_api.route('', methods=['GET'])
class GetFavoriteMoviesResource(Resource):
    """
    Resource for fetching the favorite movies of a user.
    """

    @favorite_api.response(200, "Success", model=movie_list_model)
    @favorite_api.response(200, "Success")
    @jwt_required()
    def get(self):
        """
        Get the favorite movies of a user.
        """
        # Get the ids of the favorite movies from the database
        user_id = int(get_jwt_identity())
        favorite_movies = db.session.query(FavoriteMovie).filter(FavoriteMovie.user_id == user_id).all()
        if not favorite_movies:
            return {"message": "No favorite movies found."}

        jwt = request.cookies.get("access_token_cookie")
        response = requests.get(
            "http://movie_api:5000/api/movies/list", params={
                "movie_ids": [
                    movie.movie_id for movie in favorite_movies
                ]
            },
            cookies={"access_token_cookie": jwt},
            timeout=5,
        )
        return response.json()


def register_routes(api_blueprint: Api) -> None:
    """
    Register the movies API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(favorite_api)
