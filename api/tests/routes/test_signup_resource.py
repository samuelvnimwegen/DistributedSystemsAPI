"""
This module contains tests for the signup resource of the Flask application.
"""

from src.database.models import User


def test_signup_resource(no_cookie_client, db_session):
    """
    Test the signup resource.
    :param no_cookie_client: The Flask test client without a JWT cookie
    :param db_session: The database session fixture
    :return: None
    """
    # Test that we cannot access the movies api without a JWT cookie
    response = no_cookie_client.get(
        "api/movies",
    )
    assert response.status_code == 401

    # Test that the user does not exist in the database
    user = db_session.query(User).filter_by(username="test_user_test_signup_resource").first()
    assert user is None

    # Test signup with valid credentials
    response = no_cookie_client.post(
        "api/sign_up",
        json={
            "username": "test_user_test_signup_resource",
            "password": "password"
        }
    )
    assert response.status_code == 200
    assert response.json == {"message": "User created successfully"}

    # Test that you can access the movies api
    response = no_cookie_client.get(
        "api/movies",
    )
    assert response.status_code == 200

    # Test that the user exists in the database
    user = db_session.query(User).filter_by(username="test_user_test_signup_resource").first()
    assert user is not None
