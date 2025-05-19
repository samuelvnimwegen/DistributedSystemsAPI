"""
This code is a test suite for the user resource API endpoints.
"""
import pytest

from src.database import User


@pytest.fixture
def another_user(db_session):
    """
    Create another user for testing purposes.
    """
    user = User(username="bob", password="password")
    db_session.add(user)
    db_session.commit()
    return user


def test_get_all_users(client, db_session, another_user):
    """
    Test that the GET /api/users/ endpoint returns all users.
    """
    response = client.get("/api/users/retrieve")
    assert response.status_code == 200
    data = response.get_json()
    usernames = [u["username"] for u in data["results"]]
    assert "test_user" in usernames
    assert "bob" in usernames


@pytest.mark.parametrize(
    "argument",
    [
        "{user_id}",
        "{username}",
    ],
)
def test_get_user_by_id(client, db_session, argument):
    """
    Test that the GET /api/users/<user_id or name> endpoint returns the user with the given ID.
    """
    test_user = db_session.query(User).first()
    arg = argument.format(user_id=test_user.user_id, username=test_user.username)
    url = f"/api/users/retrieve/{arg}"
    response = client.get(url)
    assert response.status_code == 200
    data = response.get_json()
    assert data["username"] == "test_user"
    assert data["user_id"] == test_user.user_id


@pytest.mark.parametrize(
    "argument",
    [9999, "nonexistent"],
)
def test_get_user_by_id_not_found(client, argument):
    """
    Test that the GET /api/users/<user_id or name> endpoint returns a 404 error when the user is not found.
    """
    response = client.get(f"/api/users/retrieve/{argument}")
    assert response.status_code == 404
    assert response.get_json() == {"message": "User not found"}
