"""
Test cases for the rating resource API endpoints.
"""
from unittest.mock import patch
from src.database import Rating, RatingReview


@patch("requests.get")
def test_post_rating_success(mock_get, client):
    """
    Test case for posting a rating when the movie is watched.
    """
    # Mock external watched check
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"results": ["dummy_entry"]}

    response = client.post(
        "/api/preference/rating/123",  # movie_id = 123
        data={"rating": 4, "review": "Great movie!"},
        headers={"X-CSRF-Token": client.csrf_token}
    )

    assert response.status_code == 200
    assert "Rating added successfully" in response.json["message"]


@patch("requests.get")
def test_post_rating_not_watched(mock_get, client):
    """
    Test case for posting a rating when the movie is not watched.
    """
    # Simulate not watched
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"results": []}

    response = client.post(
        "/api/preference/rating/123",
        data={"rating": 5, "review": "Unwatched"},
        headers={"X-CSRF-Token": client.csrf_token}
    )

    assert response.status_code == 400
    assert response.json["message"] == "Movie not watched"


@patch("requests.get")
def test_post_rating_logging_error(mock_get, client):
    """
    Test case for posting a rating when there is an error with the logging service.
    """
    # Simulate error from logging service
    mock_get.return_value.status_code = 500
    mock_get.return_value.json.return_value = {"error": "Internal Server Error"}

    response = client.post(
        "/api/preference/rating/123",
        data={"rating": 3, "review": "Error test"},
        headers={"X-CSRF-Token": client.csrf_token}
    )

    assert response.status_code == 400
    assert "error while getting watched movies" in response.json["message"]


def test_delete_rating_success(client, db_session):
    """
    Test case for deleting a rating.
    """
    # Add a rating to delete
    rating = Rating(rating=5, review="Test", user_id=1, movie_id=123)
    db_session.add(rating)
    db_session.commit()

    response = client.delete("/api/preference/rating/123", headers={"X-CSRF-Token": client.csrf_token})
    assert response.status_code == 200
    assert response.json["message"] == "Rating deleted successfully"


def test_delete_rating_not_found(client):
    """
    Test case for deleting a rating that does not exist.
    """
    response = client.delete("/api/preference/rating/999", headers={"X-CSRF-Token": client.csrf_token})
    assert response.status_code == 404
    assert response.json["message"] == "Rating does not exist"


@patch("src.routes.ratings_resource.requests.get")
def test_get_friend_ratings_success(mock_get, client, db_session):
    """
    Test case for getting friend ratings.
    """
    # Make a rating
    rating = Rating(rating=5, review="Test", user_id=2, movie_id=42)
    db_session.add(rating)
    db_session.commit()

    # Mock response from user service
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "results": [{"user_id": 2}]
    }

    response = client.get("/api/preference/rating/friends")
    assert response.status_code == 200
    data = response.get_json()
    assert "results" in data
    assert any(r["movie_id"] == 42 for r in data["results"])


def create_rating(db_session, user_id, movie_id=42):
    rating = Rating(user_id=user_id, movie_id=movie_id, rating=4.0, review="Great movie!")
    db_session.add(rating)
    db_session.commit()


def create_sample_rating(db_session, user_id=1, movie_id=42, score=4.0):
    """
    Helper function to create a sample rating for testing.
    """
    rating = Rating(user_id=user_id, movie_id=movie_id, rating=score, review="Sample review")
    db_session.add(rating)
    db_session.commit()
    return rating


def test_post_friend_review_success(client, db_session):
    """
    Test case for posting a friend review successfully.
    """
    # Arrange
    rating = create_sample_rating(db_session, user_id=2)  # friend

    # Act
    response = client.post(
        f"/api/preference/rating_review/{rating.rating_id}?agreed=True",
        headers={"X-CSRF-Token": client.csrf_token},
    )

    # Assert
    assert response.status_code == 200
    assert response.json["message"] == "Rating review added successfully"

    # Also check DB side effect
    review = db_session.query(RatingReview).filter_by(rating_id=rating.rating_id).first()
    assert review is not None
    assert review.agreed is True


def test_post_friend_review_missing_agreed(client, db_session):
    """
    Test case for posting a friend review with missing 'agreed' field.
    """
    # Arrange
    rating = create_sample_rating(db_session, user_id=2)

    # Act
    response = client.post(
        f"/api/preference/rating_review/{rating.rating_id}",
        headers={"X-CSRF-Token": client.csrf_token},
    )

    # Assert
    assert response.status_code == 400


def test_post_friend_review_not_found(client):
    """
    Test case for posting a friend review when the rating does not exist.
    """
    # Act
    response = client.post(
        "/api/preference/rating_review/9999?agreed=True",
        headers={"X-CSRF-Token": client.csrf_token},
    )

    # Assert
    assert response.status_code == 404
    assert response.json["message"] == "Rating not found"


class MockResponse:
    """
    Mock class to simulate requests.Response for testing.
    """

    def __init__(self, json_data, status_code=200):
        """
        Initialize the mock response with JSON data and status code.
        """
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        """
        Return the JSON data of the mock response.
        """
        return self._json_data
