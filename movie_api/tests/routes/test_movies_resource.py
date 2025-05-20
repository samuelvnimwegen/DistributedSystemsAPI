"""
This module contains the test cases for the movies resource.
"""
from unittest.mock import patch, MagicMock

from src.database import Movie


def mock_movie_picture(mock_object: MagicMock) -> str:
    """
    Mock function to return a fake movie picture URL.
    """
    fake_response = {"results": [{"poster_path": "/inception.jpg"}]}
    mock_response = MagicMock()
    mock_response.json.return_value = fake_response
    mock_object.return_value = mock_response


@patch("src.database.models.movie.requests.get")
def test_get_popular_movies_returns_limited_list(mock_get, client, db_session):
    """
    Test that the get_popular_movies endpoint returns a limited number of movies.
    """
    for i in range(5):
        db_session.add(Movie(movie_name=f"Movie {i}", rating=8.0, runtime=100, meta_score=75, plot="Good movie"))
    db_session.commit()

    mock_movie_picture(mock_get)

    response = client.get("/api/movies/list?amount=3")

    assert response.status_code == 200
    data = response.get_json()
    assert "results" in data
    assert len(data["results"]) == 3


@patch("src.database.models.movie.requests.get")
def test_get_movie_details_returns_correct_movie(mock_get, client, db_session):
    """
    Test that the get_movie_details endpoint returns the correct movie details.
    """
    movie = Movie(movie_name="Inception", rating=9.0, runtime=148, meta_score=90, plot="Dreams within dreams")
    db_session.add(movie)
    db_session.commit()

    mock_movie_picture(mock_get)

    response = client.get(f"/api/movies/{movie.movie_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["movie_name"] == "Inception"
