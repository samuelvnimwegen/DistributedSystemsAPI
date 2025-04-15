"""
This module contains tests for the login resource of the Flask application.
"""


def test_login_resource(no_cookie_client):
    """
    Test the login resource.

    :param no_cookie_client: The Flask test client without a JWT cookie
    """
    # Test that we cannot access the movies api without a JWT cookie
    response = no_cookie_client.get(
        "api/movies/favorite/324544",
    )
    assert response.status_code == 401

    # Test login with valid credentials (those from the fixture)
    response = no_cookie_client.post(
        "api/login",
        json={
            "username": "test_user",
            "password": "password"
        }
    )
    assert response.status_code == 200
    assert response.json == {"msg": "Login successful"}

    # Test that you can access the movies api
    response = no_cookie_client.get(
        "api/movies/favorite/324544",
    )
    assert response.status_code == 200

    # Test login with invalid credentials
    response = no_cookie_client.post(
        "api/login",
        json={
            "username": "invaliduser",
            "password": "invalidpassword"
        }
    )
    assert response.status_code == 401
    assert response.json == {"message": "Invalid username or password"}

    # Test that you can still access the movies api
    response = no_cookie_client.get(
        "api/movies/favorite/324544",
    )
    assert response.status_code == 200
