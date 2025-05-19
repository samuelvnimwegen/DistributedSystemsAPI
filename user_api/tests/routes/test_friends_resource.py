"""
Test cases for the friend resource in the user API.
"""
import pytest
from flask_restx import Api

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


def test_get_friends_returns_user_friends(client, db_session, another_user):
    """
    Test that the GET /friends endpoint returns the friends of the current user.
    """
    user = db_session.query(User).first()
    user.add_friend(another_user)
    db_session.commit()

    response = client.get("/api/users/friends")
    results = response.json.get("results")
    assert response.status_code == 200
    assert len(results) == 1
    assert results[0]["username"] == another_user.username
    assert results[0]["user_id"] == another_user.user_id


def test_post_add_friend_success(client, db_session, another_user):
    """
    Test that the POST /friends endpoint adds a friend successfully.
    """
    test_user = db_session.query(User).first()
    response = client.post("/api/users/friends", json={"username": "bob"}, headers={"X-CSRF-Token": client.csrf_token})

    assert response.status_code == 200
    assert response.json == {"message": "Friend added successfully"}

    db_session.refresh(test_user)
    assert another_user in test_user.get_friends()


def test_post_add_friend_not_found(client):
    """
    Test that the POST /friends endpoint returns a 404 error when the user is not found.
    """
    response = client.post(
        "/api/users/friends",
        headers={"X-CSRF-Token": client.csrf_token},
        json={"username": "nonexistent"}
    )

    assert response.status_code == 404
    assert response.json == {"message": "User with username 'nonexistent' not found"}
