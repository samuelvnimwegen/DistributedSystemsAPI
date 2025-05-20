"""
This module contains the API routes for managing ratings and reviews of movies.
"""
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, marshal, Api

from src.database import db
from src.database import RatingReview, Rating
from src.routes.ratings_resource import rating_model, rating_review_parser, rating_review_list_model

rating_review_ns = Namespace("rating_review", description="Rating and review operations")


@rating_review_ns.route("/<int:rating_id>")
class RatingReviewResource(Resource):
    """
    Resource for managing rating reviews.
    """

    @rating_review_ns.response(200, "Success", rating_review_list_model)
    @rating_review_ns.response(400, "Bad Request")
    @rating_review_ns.response(401, "Unauthorized")
    @rating_review_ns.response(404, "Not Found")
    @jwt_required()
    def get(self, rating_id):
        """
        Get all the rating reviews for a rating.
        """
        # Get the rating reviews
        rating_reviews = db.session.query(RatingReview).filter(RatingReview.rating_id == rating_id).all()
        if not rating_reviews:
            return {"results": []}, 200

        return marshal({"results": rating_reviews}, rating_review_list_model), 200

    @rating_review_ns.expect(rating_review_parser)
    @rating_review_ns.response(200, "Success", rating_model)
    @rating_review_ns.response(400, "Bad Request")
    @rating_review_ns.response(401, "Unauthorized")
    @rating_review_ns.response(404, "Not Found")
    @jwt_required()
    def post(self, rating_id):
        """
        Post a review for a rating from a friend.
        """
        user_id = int(get_jwt_identity())
        args = rating_review_parser.parse_args(request)
        agreed: bool = args.get("agreed", None)
        if not agreed:
            return {"message": "Agreed value is required, either True or False"}, 400

        # Get the movie ID from the request arguments
        rating: Rating = db.session.query(Rating).filter(Rating.rating_id == rating_id).first()

        if not rating:
            return {"message": "Rating not found"}, 404

        # Make a rating review
        rating_review = RatingReview(user_id=user_id, rating_id=rating_id, agreed=agreed)
        db.session.add(rating_review)
        db.session.commit()

        return {"message": "Rating review added successfully"}, 200


@rating_review_ns.route("")
class FriendReviewResource(Resource):
    """
    Resource for getting rating reviews from the user
    """

    @rating_review_ns.expect(rating_review_parser)
    @rating_review_ns.response(200, "Success", rating_review_list_model)
    @rating_review_ns.response(400, "Bad Request")
    @rating_review_ns.response(401, "Unauthorized")
    @rating_review_ns.response(404, "Not Found")
    @jwt_required()
    def get(self):
        """
        Get all the rating reviews for the current user.
        """
        # Get the rating reviews
        user_id = int(get_jwt_identity())
        rating_reviews = db.session.query(RatingReview).filter(RatingReview.user_id == user_id).all()
        if not rating_reviews:
            return {"results": []}, 200

        return marshal({"results": rating_reviews}, rating_review_list_model), 200


def register_routes(api_blueprint: Api) -> None:
    """
    Register the movies API routes with the provided Flask application blueprint.

    :param api_blueprint: The Flask application blueprint
    :return: None
    """
    api_blueprint.add_namespace(rating_review_ns)
