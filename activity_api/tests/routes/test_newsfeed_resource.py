"""
This code is a test suite for the newsfeed resource API endpoints.
"""
from unittest.mock import patch, MagicMock


@patch("src.routes.newsfeed_resource.requests.get")
@patch("src.routes.newsfeed_resource.db.session.query")
def test_get_newsfeed_success(mock_query, mock_requests, client):
    """
    Test the successful retrieval of the newsfeed.
    """
    # Mock the user service response
    mock_requests.return_value = MagicMock(
        status_code=200,
        json=lambda: {"results": [{"user_id": 2}, {"user_id": 3}]}
    )

    # Mock database query
    mock_result = MagicMock()
    mock_result.user_id = 2
    mock_result.movie_id = 1
    mock_result.watched_at = "2024-01-01T12:00:00"
    mock_query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_result]

    response = client.get("/api/activity/newsfeed/")

    assert response.status_code == 200
    assert "results" in response.json
    assert isinstance(response.json["results"], list)


@patch("src.routes.newsfeed_resource.requests.get")
def test_get_newsfeed_friends_api_error(mock_requests, client):
    mock_requests.return_value = MagicMock(
        status_code=500,
        json=lambda: {"error": "User service down"}
    )

    response = client.get("/api/activity/newsfeed/")

    assert response.status_code == 500
    assert "message" in response.json
    assert "Failed to fetch friends" in response.json["message"]


@patch("src.routes.newsfeed_resource.requests.get")
def test_get_newsfeed_no_friends(mock_requests, client):
    mock_requests.return_value = MagicMock(
        status_code=200,
        json=lambda: {"results": []}
    )

    response = client.get("/api/activity/newsfeed/")

    assert response.status_code == 200
    assert response.json == {"results": []}


@patch("src.routes.newsfeed_resource.requests.get")
@patch("src.routes.newsfeed_resource.db.session.query")
def test_get_newsfeed_no_movies(mock_query, mock_requests, client):
    mock_requests.return_value = MagicMock(
        status_code=200,
        json=lambda: {"results": [{"user_id": 2, "watched_at": "2024-01-01T12:00:00", "movie_id": 1}]}
    )

    mock_query.return_value.filter.return_value.order_by.return_value.all.return_value = []

    response = client.get("/api/activity/newsfeed/")

    assert response.status_code == 200
    assert response.json == {"results": []}
