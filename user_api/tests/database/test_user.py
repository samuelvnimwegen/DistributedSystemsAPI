"""
Test cases for the User model in the database.
"""
import pytest
from sqlalchemy.orm import Session
from src.database.models.user import User


def test_add_and_get_friends(db_session: Session):
    """
    Test adding and getting friends for a user.
    """
    user1 = User(username="alice", password="password123")
    user2 = User(username="bob", password="password456")

    db_session.add_all([user1, user2])
    db_session.commit()

    user1.add_friend(user2)
    db_session.commit()

    assert user2 in user1.get_friends()
    assert user1 in user2.get_friends()


def test_remove_friend(db_session: Session):
    """
    Test removing a friend from a user.
    """
    user1 = User(username="charlie", password="pass")
    user2 = User(username="dave", password="word")

    db_session.add_all([user1, user2])
    db_session.commit()

    user1.add_friend(user2)
    db_session.commit()

    assert user1 in user2.get_friends()
    assert user2 in user1.get_friends()

    user1.remove_friend(user2)
    db_session.commit()

    assert user1 not in user2.get_friends()
    assert user2 not in user1.get_friends()


def test_add_self_as_friend_raises(db_session: Session):
    """
    Test that adding oneself as a friend raises an AssertionError.
    """
    user = User(username="eva", password="securepass")
    db_session.add(user)
    db_session.commit()

    with pytest.raises(AssertionError):
        user.add_friend(user)


def test_friend_type_check_raises(db_session: Session):
    """
    Test that adding a non-User instance as a friend raises an AssertionError.
    """
    user = User(username="felix", password="abc")
    db_session.add(user)
    db_session.commit()

    with pytest.raises(AssertionError):
        user.add_friend("not-a-user")

    with pytest.raises(AssertionError):
        user.remove_friend("not-a-user")


def test_check_password():
    """
    Test the check_password method of the User class.
    """
    user = User(username="greg", password="mypass")
    assert user.check_password("mypass")
    assert not user.check_password("wrongpass")
