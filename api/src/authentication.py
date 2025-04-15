"""
This module contains the authentication logic for the application.
"""
from typing import Optional
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, set_access_cookies, get_jwt
from flask import Flask, Response
from src.database.models.user import User
from src.database.database import db


def add_user_identity_lookup(jwt: JWTManager) -> None:
    """
    Add custom user identity loader to use the get_jwt_identity() function from the JWT manager

    This function is used to load the user identity (user_id) from user object the above function returns.
    """

    @jwt.user_identity_loader
    def user_identity_lookup(user: User) -> str:
        return str(user.user_id)


def add_user_lookup_callback(jwt: JWTManager) -> None:
    """
    Add custom user loader to use the get_current_user() function from the JWT manager

    This function is used to load the user from the JWT token.
    """

    @jwt.user_lookup_loader
    def user_lookup_loader(_jwt_header: dict[str, str], jwt_data: dict[str, str]) -> Optional[User]:
        identity = jwt_data["sub"]
        user: Optional[User] = db.session.query(User).filter(User.user_id == int(identity)).first()
        return user


def add_cookie_refresher(app: Flask) -> None:
    """
    Add custom cookie refresher to use the get_jwt_identity() function from the JWT manager

    This function is used to refresh the JWT token when it is about to expire.
    """

    # Using an `after_request` callback, we refresh any token within 30 minutes of expiring.
    # Change the time-deltas to match the needs of your application.
    @app.after_request
    def refresh_expiring_jwts(response: Response) -> Response:
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
            return response
        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Return the original response
            return response
