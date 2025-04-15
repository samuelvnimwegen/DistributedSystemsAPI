"""
This module contains tests for the logout resource.
"""


def test_logout_resource(client):
    """
    Test the logout resource.
    :param client: The Flask test client with a JWT cookie
    :return: None
    """
    # Test that we can access the movies api with a JWT cookie
    response = client.get(
        "api/movies/favorite/324544",
    )
    assert response.status_code == 200

    # Test logout
    response = client.post(
        "api/logout",
    )
    assert response.status_code == 200
    assert response.json == {"msg": "Logout successful"}

    # Test that we cannot access the movies api without a JWT cookie
    response = client.get(
        "api/movies/favorite/324544",
    )
    assert response.status_code == 401
