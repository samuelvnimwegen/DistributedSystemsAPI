"""
Test cases for the recommendation resource.
"""
from unittest.mock import patch, Mock


@patch("src.routes.recommendation_resource.requests.get")
def test_get_recommendations_success(mock_get, client):
    """
    Test case for getting movie recommendations successfully.
    """
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"results": [{"movie_id": 1, "title": "Movie A"}]}

    response = client.get("/api/preference/recommendations", query_string={"amount": 1})

    assert response.status_code == 200
    assert response.json == {"results": [{"movie_id": 1, "title": "Movie A"}]}
    mock_get.assert_called_once()


@patch("src.routes.recommendation_resource.requests.get")
def test_get_recommendations_fail(mock_get, client):
    """
    Test case for getting movie recommendations when the movie API fails.
    """
    mock_get.return_value.status_code = 500

    response = client.get("/api/preference/recommendations", query_string={"amount": 1})

    assert response.status_code == 500
    assert response.json == {"message": "Failed to fetch movie list."}


@patch("src.routes.recommendation_resource.requests.get")
def test_get_friends_recommendations_success(mock_get, client):
    """
    Test case for getting movie recommendations based on friends' ratings.
    """
    def side_effect(url, *_, **__):
        """
        Mock responses for different API calls.
        """
        if "user_api" in url:
            mock = Mock()
            mock.status_code = 200
            mock.json.return_value = {"results": [{"user_id": 2}, {"user_id": 3}]}
            return mock
        if "logging_api" in url:
            mock = Mock()
            mock.status_code = 200
            mock.json.return_value = {
                "results": [{"movie_id": 1, "user_id": 2}, {"movie_id": 1, "user_id": 3}]
            }
            return mock
        if "movie_api" in url:
            mock = Mock()
            mock.status_code = 200
            mock.json.return_value = {"results": [{"movie_id": 1, "title": "Movie A"}]}
            return mock
        return Mock(status_code=404)

    mock_get.side_effect = side_effect

    response = client.get("/api/preference/recommendations/friends", query_string={"amount": 1})

    assert response.status_code == 200
    assert response.json == {"results": [{"movie_id": 1, "title": "Movie A"}]}


@patch("src.routes.recommendation_resource.requests.get")
def test_get_friends_recommendations_fail_on_friends_api(mock_get, client):
    """
    Test case for getting movie recommendations based on friends' ratings when the friends API fails.
    """
    mock_get.return_value.status_code = 500

    response = client.get("/api/preference/recommendations/friends", query_string={"amount": 1})

    assert response.status_code == 500
    assert response.json == {"message": "Failed to fetch friends list."}
