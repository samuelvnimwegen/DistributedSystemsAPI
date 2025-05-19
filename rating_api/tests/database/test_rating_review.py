"""
Test cases for the RatingReview model.
"""
import pytest
from src.database.models.rating_review import RatingReview


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
