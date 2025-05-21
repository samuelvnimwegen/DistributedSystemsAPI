"""
This module defines the error handlers for the Flask application.
"""
from flask import jsonify, Flask, Response
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError


# pylint: disable=unused-argument
# type: ignore

def register_error_handlers(jwt_manager: JWTManager, flask_app: Flask) -> None:
    """
    Register custom error handlers for the Flask application.

    :param jwt_manager: The JWT manager to attach to
    :param flask_app: The Flask application instance
    """

    @jwt_manager.unauthorized_loader
    def unauthorized_callback(error) -> tuple[Response, int]:
        """
        Handle unauthorized requests.
        :return:
        """
        return jsonify({"message": "Unauthorized"}), 401

    @jwt_manager.expired_token_loader
    def expired_token_callback(error) -> tuple[Response, int]:
        """
        Handle expired tokens.
        :return:
        """
        return jsonify({"message": "Expired token (log back in)"}), 401

    @jwt_manager.invalid_token_loader
    def invalid_token_callback(error) -> tuple[Response, int]:
        """
        Handle invalid tokens.
        :return:
        """
        return jsonify({"message": "Invalid token (check format?)"}), 401

    @jwt_manager.token_verification_failed_loader
    def token_verification_failed_callback(error) -> tuple[Response, int]:
        """
        Handle token verification failures.
        :return:
        """
        return jsonify({"message": "Token verification failed"}), 401

    @flask_app.errorhandler(NoAuthorizationError)
    def handle_no_auth_error(error: NoAuthorizationError) -> tuple[Response, int]:
        """
        Handle missing authorization cookies errors.
        :return:
        """
        return jsonify({"message": "Missing authorization cookies"}), 401
