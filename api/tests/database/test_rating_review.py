"""
Test cases for the RatingReview model.
"""
import pytest
from src.database.models.user import User
from src.database.models.movie import Movie
from src.database.models.rating import Rating
from src.database.models.rating_review import RatingReview

def test_create_valid_rating_review(db_session):
    """
    Test creating a valid RatingReview instance.
    """
    # Set up dependencies
    user = User(username="alice", password="test")
    movie = Movie(movie_name="Dune", rating=8.4, runtime=155, meta_score=83, plot="Sci-fi epic.")
    db_session.add_all([user, movie])
    db_session.commit()

    rating = Rating(rating=9.0, user_id=user.user_id, movie_id=movie.movie_id)
    db_session.add(rating)
    db_session.commit()

    reviewer = User(username="bob", password="test")
    db_session.add(reviewer)
    db_session.commit()

    # Create RatingReview
    review = RatingReview(user_id=reviewer.user_id, rating_id=rating.rating_id, agreed=True)
    db_session.add(review)
    db_session.commit()

    fetched = db_session.query(RatingReview).first()
    assert fetched is not None
    assert fetched.agreed is True
    assert fetched.user_id == reviewer.user_id
    assert fetched.rating_id == rating.rating_id

def test_invalid_user_id_type():
    """
    Test creating a RatingReview instance with an invalid user_id type.
    """
    with pytest.raises(AssertionError, match="User ID must be an integer"):
        RatingReview(user_id="abc", rating_id=1, agreed=True)

def test_invalid_rating_id_type():
    """
    Test creating a RatingReview instance with an invalid rating_id type.
    """
    with pytest.raises(AssertionError, match="Rating ID must be an integer"):
        RatingReview(user_id=1, rating_id="xyz", agreed=True)

def test_invalid_agreed_type():
    """
    Test creating a RatingReview instance with an invalid agreed type.
    """
    with pytest.raises(AssertionError, match="Agreed must be a boolean"):
        RatingReview(user_id=1, rating_id=1, agreed="yes")

def test_invalid_user_id_value():
    """
    Test creating a RatingReview instance with an invalid user_id value.
    """
    with pytest.raises(AssertionError, match="User ID must be greater than 0"):
        RatingReview(user_id=0, rating_id=1, agreed=True)

def test_invalid_rating_id_value():
    """
    Test creating a RatingReview instance with an invalid rating_id value.
    """
    with pytest.raises(AssertionError, match="Rating ID must be greater than 0"):
        RatingReview(user_id=1, rating_id=0, agreed=False)

def test_relationships(db_session):
    """
    Test the relationships between RatingReview, User, and Rating.
    """
    user = User(username="testuser", password="test")
    movie = Movie(movie_name="Interstellar", rating=9.0, runtime=169, meta_score=88, plot="Space exploration.")
    db_session.add_all([user, movie])
    db_session.commit()

    rating = Rating(rating=8.5, user_id=user.user_id, movie_id=movie.movie_id)
    reviewer = User(username="reviewer", password="test")
    db_session.add_all([rating, reviewer])
    db_session.commit()

    review = RatingReview(user_id=reviewer.user_id, rating_id=rating.rating_id, agreed=False)
    db_session.add(review)
    db_session.commit()

    fetched = db_session.query(RatingReview).first()
    assert fetched.user.username == "reviewer"
    assert fetched.rating.rating == 8.5
