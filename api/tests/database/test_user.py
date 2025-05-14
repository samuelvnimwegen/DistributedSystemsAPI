"""
Test cases for the User model in the database.
"""
import datetime
import pytest
from sqlalchemy.orm import Session
from src.database import Movie, WatchedMovie
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


def test_users_watched_relationship(db_session):
    """
    Test the relationship between User and Movie through the users_watched association table.
    """
    # Create a user and a movie
    user = User(username="alice", password="secure")
    movie = Movie(
        movie_name="The Matrix Part 2",
        rating=8.7,
        runtime=136,
        meta_score=73,
        plot="A computer hacker learns about the true nature of reality."
    )

    # Set up relationship
    movie.users_watched.append(user)
    db_session.add_all([user, movie])
    db_session.commit()

    # Refresh and assert
    db_session.refresh(movie)
    db_session.refresh(user)

    assert user in movie.users_watched
    assert movie in user.watched_movies
    assert len(user.watched_movie_associations) == 1
    assert len(movie.users_watched) == 1
    assert len(user.watched_movies) == 1
    assert len(user.watched_movie_associations) == 1
    assert user.watched_movie_associations[0].movie_id == movie.movie_id
    assert user.watched_movie_associations[0].watched_at is not None


def test_get_latest_watched_by_friends_returns_sorted_subset(db_session):
    """
    Test that get_latest_watched_by_friends returns the latest watched movies by friends,
    """
    # Create main user and 2 friends
    user = User(username="main_user", password="test")
    friend1 = User(username="friend1", password="test")
    friend2 = User(username="friend2", password="test")
    db_session.add_all([user, friend1, friend2])
    db_session.commit()

    # Mock the method get_friends
    user.get_friends = lambda: [friend1, friend2]

    # Create some movies
    movie1 = Movie(movie_name="Movie 1", rating=8.0, runtime=120, meta_score=70, plot="A great movie.")
    movie2 = Movie(movie_name="Movie 2", rating=7.5, runtime=130, meta_score=65, plot="Another great movie.")
    movie3 = Movie(movie_name="Movie 3", rating=9.0, runtime=140, meta_score=80, plot="An amazing movie.")
    db_session.add_all([movie1, movie2, movie3])
    db_session.commit()

    # Create watched movie associations with watched_at timestamps
    wm1 = WatchedMovie(user=friend1, movie=movie1, watched_at=datetime.datetime(2024, 5, 1))
    wm2 = WatchedMovie(user=friend2, movie=movie2, watched_at=datetime.datetime(2024, 5, 3))
    wm3 = WatchedMovie(user=friend1, movie=movie3, watched_at=datetime.datetime(2024, 5, 2))
    db_session.add_all([wm1, wm2, wm3])
    db_session.commit()

    # Assign watched associations
    friend1.watched_movie_associations = [wm1, wm3]
    friend2.watched_movie_associations = [wm2]
    user.watched_movie_associations = []
    db_session.commit()

    # Call method
    result = User.get_latest_watched_by_friends(user, amount=2)

    # Check that results are sorted by watched_at desc and limited to 2
    assert len(result) == 2
    assert result[0] == wm2  # Newest
    assert result[1] == wm3  # Second newest


def test_get_latest_watched_by_friends_with_no_friends_returns_empty():
    """
    Test that get_latest_watched_by_friends returns an empty list if the user has no friends.
    """
    user = User(username="lonely_user", password="test")
    user.get_friends = lambda: []

    result = User.get_latest_watched_by_friends(user)
    assert not result
