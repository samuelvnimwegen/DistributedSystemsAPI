from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, Api

favorite_api = Namespace('favorite', description='Favorite movies related operations')


@favorite_api.route('/favorite/<int:movie_id>')
class ChangeFavoriteResource(Resource):
    """
    Resource for changing the favorite status of a movie.
    """

    @jwt_required()
    def post(self, movie_id):
        """
        Add a movie to the favorite list.
        """
        # if not user:
        #     movies_api.abort(401, "User not authenticated.")
        #
        # # Get the movie
        # movie: Movie = db.session.query(Movie).filter_by(movie_id=movie_id).first()
        # if not movie:
        #     movies_api.abort(404, "Movie not found.")
        #
        # # Check if the movie is already in the favorite list
        # if movie in user.favorite_movies:
        #     return {"message": "Movie is already in favorites."}
        #
        # # Add the movie to the favorite list
        # user.favorite_movies.append(movie)
        # db.session.commit()

        return {"message": "Movie added to favorites."}

    @jwt_required()
    def delete(self, movie_id):
        """
        Remove a movie from the favorite list.
        """
        # user: User = get_current_user()
        # if not user:
        #     movies_api.abort(401, "User not authenticated.")
        #
        # # Get the movie
        # movie: Movie = db.session.query(Movie).filter_by(movie_id=movie_id).first()
        # if not movie:
        #     movies_api.abort(404, "Movie not found.")
        #
        # # Check if the movie is in the favorite list
        # if movie not in user.favorite_movies:
        #     return {"message": "Movie is not in favorites."}
        #
        # # Remove the movie from the favorite list
        # user.favorite_movies.remove(movie)
        # db.session.commit()

        return {"message": "Movie removed from favorites."}

    @favorite_api.doc(params={"movie_id": "The ID of the movie to check if it's a favorite."})
    @favorite_api.response(200, "Success")
    @jwt_required()
    def get(self, movie_id):
        """
        Get the favorite status of a movie. This is whether the movie is in the favorite list or not.
        """
        # user: User = get_current_user()
        # if not user:
        #     movies_api.abort(401, "User not authenticated.")
        #
        # # Get the movie
        # movie: Movie = db.session.query(Movie).filter_by(movie_id=movie_id).first()
        # if not movie:
        #     movies_api.abort(404, "Movie not found.")
        #
        # # Check if the movie is in the favorite list
        # is_favorite = movie in user.favorite_movies
        #
        # return marshal({"is_favorite": is_favorite}, is_favorite_model)
        return {"message": "Movie favorite status checked."}


@favorite_api.route('/favorite', methods=['GET'])
class GetFavoriteMoviesResource(Resource):
    """
    Resource for fetching the favorite movies of a user.
    """

    @favorite_api.response(200, "Success")
    @jwt_required()
    def get(self):
        """
        Get the favorite movies of a user.
        """
        # user: User = get_current_user()
        # if not user:
        #     movies_api.abort(401, "User not authenticated.")
        #
        # # Get the favorite movies of the user
        # favorite_movies: list[Movie] = user.favorite_movies
        #
        # return marshal({"results": favorite_movies}, movie_list_model)
        return {"message": "Favorite movies fetched."}


def register_routes(api_blueprint: Api) -> None:
    """
    Register the movies API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(favorite_api)
