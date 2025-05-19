"""
Test cases for the Rating model in the database.
"""
import pytest
from src.database.models.rating import Rating




def test_invalid_rating_below_range():
    """
    Test creating a Rating instance with an invalid rating value (below range).
    """
    with pytest.raises(AssertionError):
        Rating(rating=0.0, user_id=1, movie_id=1, review="")


def test_invalid_rating_above_range():
    """
    Test creating a Rating instance with an invalid rating value (above range).
    """
    with pytest.raises(AssertionError):
        Rating(rating=10.5, user_id=1, movie_id=1, review="")


def test_invalid_user_id_type():
    """
    Test creating a Rating instance with an invalid user_id type.
    """
    with pytest.raises(AssertionError):
        Rating(rating=7.5, user_id="one", movie_id=1, review="")


def test_invalid_movie_id_type():
    """
    Test creating a Rating instance with an invalid movie_id type.
    """
    with pytest.raises(AssertionError):
        Rating(rating=7.5, user_id=1, movie_id="one", review="")
