"""
This module contains the recommendation resource routes.
"""

import requests
from flask import request
from flask_restx import Namespace, Resource, Api
from flask_jwt_extended import jwt_required
from src.routes.favorite_resource import movie_list_model

recommendation_ns = Namespace("recommendations", description="Recommendation operations")

rating_parser = recommendation_ns.parser()
rating_parser.add_argument(
    "amount", type=int, default=1, help="Number of popular movies to fetch, minimum 1, maximum 20", required=False
)


@recommendation_ns.route("")
class RecommendationResource(Resource):
    """
    Resource for getting movie recommendations based on audience ratings.
    """

    @recommendation_ns.expect(rating_parser)
    @recommendation_ns.response(200, "Success", movie_list_model)
    @recommendation_ns.response(400, "Bad Request")
    @recommendation_ns.response(401, "Unauthorized")
    @jwt_required()
    def get(self):
        """
        Get movie recommendations based on user ratings.
        """
        args = rating_parser.parse_args()
        amount = args.get("amount", 1)
        response = requests.get(
            "http://movie_api:5000/api/movies/list",
            cookies={"access_token_cookie": request.cookies.get("access_token_cookie")},
            params={"amount": amount},
            timeout=5,
        )
        if response.status_code != 200:
            return {"message": "Failed to fetch movie list."}, response.status_code

        return response.json(), 200


@recommendation_ns.route("/friends")
class FriendsRecommendationResource(Resource):
    """
    Resource for getting movie recommendations based on friends' ratings.
    """

    @recommendation_ns.expect(rating_parser)
    @recommendation_ns.response(200, "Success")
    @recommendation_ns.response(400, "Bad Request")
    @recommendation_ns.response(401, "Unauthorized")
    @jwt_required()
    def get(self):
        """
        Get movie recommendations based on what friends watched recently.
        """
        args = rating_parser.parse_args()
        amount = args.get("amount", 1)

        # Send a request to the friends API to get the list of friends
        response = requests.get(
            "http://user_api:5003/api/users/friends",
            cookies={"access_token_cookie": request.cookies.get("access_token_cookie")},
            timeout=5,
        )
        if response.status_code != 200:
            return {"message": "Failed to fetch friends list."}, response.status_code

        friends = response.json().get("results", [])
        friend_ids = [friend["user_id"] for friend in friends]

        if not friend_ids:
            return {"results": []}, 200

        # Get the movies that friends watched
        response = requests.get(
            "http://activity_api:5001/api/activity/watched",
            cookies={"access_token_cookie": request.cookies.get("access_token_cookie")},
            params={"user_id": friend_ids},
            timeout=5,
        )
        if response.status_code != 200:
            return {"message": "Failed to fetch friends' watched movies."}, response.status_code

        results = response.json().get("results", [])
        movie_id_counter = {}
        for result in results:
            movie_id = result["movie_id"]
            if movie_id not in movie_id_counter:
                movie_id_counter[movie_id] = 0
            movie_id_counter[movie_id] += 1

        # Sort the movies by the number of friends who watched them
        sorted_movies = sorted(movie_id_counter.items(), key=lambda x: x[1], reverse=True)
        sorted_movie_ids = [movie[0] for movie in sorted_movies[:amount]]

        if not sorted_movie_ids:
            return {"results": []}, 200

        # Get the movies from the id list
        response = requests.get(
            "http://movie_api:5000/api/movies/list",
            cookies={"access_token_cookie": request.cookies.get("access_token_cookie")},
            params={"movie_ids": sorted_movie_ids},
            timeout=5,
        )

        return response.json(), 200


def register_routes(api_blueprint: Api) -> None:
    """
    Register the movies API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(recommendation_ns)
