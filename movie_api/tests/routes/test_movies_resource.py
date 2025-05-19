"""
This module contains the test cases for the movies resource.
"""
from unittest.mock import patch, MagicMock

from src.database import Movie, Genre


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

    response = client.get("/api/movies?amount=3")

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


@patch("src.database.models.movie.requests.get")
def test_get_same_genre_movies(mock_get, client, db_session):
    """
    Test that the get_same_genre_movies endpoint returns movies of the same genre.
    """
    genre = Genre(genre_name="Action")
    db_session.add(genre)
    movie1 = Movie(movie_name="Movie A", rating=8.0, runtime=110, meta_score=80, plot="Plot A")
    movie2 = Movie(movie_name="Movie B", rating=7.5, runtime=105, meta_score=78, plot="Plot B")
    db_session.add_all([movie1, movie2])
    movie1.genres.append(genre)
    movie2.genres.append(genre)
    db_session.commit()

    mock_movie_picture(mock_get)

    response = client.get(f"/api/movies/{movie1.movie_id}/same_genres")
    assert response.status_code == 200
    data = response.get_json()
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["movie_name"] == "Movie B"


@patch("src.database.models.movie.requests.get")
def test_get_similar_runtime_movies(mock_get, client, db_session):
    """
    Test that the get_similar_runtime_movies endpoint returns movies with similar runtime.
    """
    movie1 = Movie(movie_name="Movie A", rating=8.0, runtime=100, meta_score=80, plot="Plot A")
    movie2 = Movie(movie_name="Movie B", rating=7.5, runtime=105, meta_score=78, plot="Plot B")
    movie3 = Movie(movie_name="Movie C", rating=6.0, runtime=140, meta_score=65, plot="Plot C")
    db_session.add_all([movie1, movie2, movie3])
    db_session.commit()

    mock_movie_picture(mock_get)

    response = client.get(f"/api/movies/{movie1.movie_id}/similar_runtime")
    assert response.status_code == 200
    data = response.get_json().get("results", [])
    returned_names = [movie["movie_name"] for movie in data]
    assert "Movie B" in returned_names
    assert "Movie C" not in returned_names
