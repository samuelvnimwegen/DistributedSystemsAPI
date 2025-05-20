"""
Test cases for the friend resource in the user API.
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


def test_get_friends_returns_user_friends(client, db_session, another_user):  # pylint: disable=redefined-outer-name
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


def test_post_add_friend_success(client, db_session, another_user):  # pylint: disable=redefined-outer-name
    """
    Test that the POST /friends endpoint adds a friend successfully.
    """
    test_user = db_session.query(User).first()
    response = client.post("/api/users/friends/bob", headers={"X-CSRF-Token": client.csrf_token})

    assert response.status_code == 200
    assert response.json == {"message": "Friend added successfully"}

    db_session.refresh(test_user)
    assert another_user in test_user.get_friends()


def test_post_add_friend_not_found(client):
    """
    Test that the POST /friends endpoint returns a 404 error when the user is not found.
    """
    response = client.post(
        "/api/users/friends/nonexistent",
        headers={"X-CSRF-Token": client.csrf_token},
    )

    assert response.status_code == 404
    assert response.json == {"message": "User with username 'nonexistent' not found"}


def test_delete_friend_success(client, db_session, another_user):  # pylint: disable=redefined-outer-name
    """
    Test that the DELETE /friends/<friend_name> endpoint successfully removes a friend.
    """
    user = db_session.query(User).first()
    user.add_friend(another_user)
    db_session.commit()

    response = client.delete(
        f"/api/users/friends/{another_user.username}",
        headers={"X-CSRF-Token": client.csrf_token},
    )

    assert response.status_code == 200
    assert response.json == {"message": "Friend removed successfully"}

    db_session.refresh(user)
    assert another_user not in user.get_friends()


def test_delete_friend_not_found(client):
    """
    Test that the DELETE /friends/<friend_name> endpoint returns 404 if the friend does not exist.
    """
    response = client.delete(
        "/api/users/friends/nonexistent_user",
        headers={"X-CSRF-Token": client.csrf_token},
    )

    assert response.status_code == 404
    assert response.json == {"message": "User with username 'nonexistent_user' not found"}
