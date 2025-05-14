"""
Test cases for the Rating model in the database.
"""
import pytest
from src.database.models.rating import Rating
from src.database.models.user import User
from src.database.models.movie import Movie

def test_create_valid_rating(db_session):
    """
    Test creating a valid Rating instance.
    """
    user = User(username="sam", password="test")
    movie = Movie(movie_name="Tenet", rating=7.5, runtime=150, meta_score=69, plot="Time travel heist.")

    db_session.add_all([user, movie])
    db_session.commit()

    rating = Rating(rating=8.0, user_id=user.user_id, movie_id=movie.movie_id)
    db_session.add(rating)
    db_session.commit()

    fetched = db_session.query(Rating).first()
    assert fetched is not None
    assert fetched.rating == 8.0
    assert fetched.user_id == user.user_id
    assert fetched.movie_id == movie.movie_id

def test_rating_relationships(db_session):
    """
    Test the relationships between Rating, User, and Movie.
    """
    user = User(username="sam", password="test")
    movie = Movie(movie_name="Oppenheimer", rating=9.0, runtime=180, meta_score=89, plot="Manhattan Project drama.")
    rating = Rating(rating=9.5, user_id=1, movie_id=1)

    user.ratings.append(rating)
    movie.ratings.append(rating)

    db_session.add_all([user, movie, rating])
    db_session.commit()

    fetched_rating = db_session.query(Rating).first()
    assert fetched_rating.user.username == "sam"
    assert fetched_rating.movie.movie_name == "Oppenheimer"

def test_invalid_rating_below_range():
    """
    Test creating a Rating instance with an invalid rating value (below range).
    """
    with pytest.raises(AssertionError):
        Rating(rating=0.0, user_id=1, movie_id=1)

def test_invalid_rating_above_range():
    """
    Test creating a Rating instance with an invalid rating value (above range).
    """
    with pytest.raises(AssertionError):
        Rating(rating=10.5, user_id=1, movie_id=1)

def test_invalid_user_id_type():
    """
    Test creating a Rating instance with an invalid user_id type.
    """
    with pytest.raises(AssertionError):
        Rating(rating=7.5, user_id="one", movie_id=1)

def test_invalid_movie_id_type():
    """
    Test creating a Rating instance with an invalid movie_id type.
    """
    with pytest.raises(AssertionError):
        Rating(rating=7.5, user_id=1, movie_id="one")
