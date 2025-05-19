"""
This file contains tests for the Movie model in the database.
"""
from unittest.mock import MagicMock, patch

import pytest

from src.database.models import Movie, Genre


def test_create_valid_movie():
    """
    Test creating a valid Movie instance.
    """
    movie = Movie(movie_name="Inception", rating=8.8, runtime=148, meta_score=74,
                  plot="A thief steals corporate secrets using dream-sharing technology.")

    assert movie.movie_name == "Inception"
    assert movie.rating == 8.8
    assert movie.runtime == 148
    assert movie.meta_score == 74
    assert movie.plot.startswith("A thief")
    assert isinstance(movie.genres, list)


def test_repr_method():
    """
    Test the __repr__ method of the Movie class.
    """
    movie = Movie(movie_name="Inception", rating=8.8, runtime=148, meta_score=74, plot="A plot.")
    movie.movie_id = 1  # Simulate primary key being set
    assert repr(movie) == "<Movie(movie_id=1, movie_name='Inception', rating=8.8, runtime=148)>"


def test_add_genre(db_session):
    """
    Test adding a genre to a Movie instance.
    """
    genre = Genre(genre_name="Sci-Fi")
    db_session.add(genre)
    db_session.commit()

    movie = Movie(movie_name="Inception", rating=8.8, runtime=148, meta_score=74, plot="A plot.")
    movie.genres.append(genre)

    assert genre in movie.genres


def test_invalid_movie_name_type():
    """
    Test creating a Movie instance with an invalid movie_name type.
    """
    with pytest.raises(AssertionError, match="movie_name must be a string"):
        Movie(movie_name=123, rating=8.8, runtime=148, meta_score=74, plot="Plot")


def test_invalid_rating_value():
    """
    Test creating a Movie instance with an invalid rating value.
    """
    with pytest.raises(AssertionError, match="rating must be non-negative"):
        Movie(movie_name="Test", rating=-1, runtime=148, meta_score=74, plot="Plot")


def test_invalid_runtime_value():
    """
    Test creating a Movie instance with an invalid runtime value.
    """
    with pytest.raises(AssertionError, match="runtime must be positive"):
        Movie(movie_name="Test", rating=5.0, runtime=0, meta_score=74, plot="Plot")


def test_invalid_meta_score_value():
    """
    Test creating a Movie instance with an invalid meta_score value.
    """
    with pytest.raises(AssertionError, match="meta_score must be less than or equal to 100"):
        Movie(movie_name="Test", rating=5.0, runtime=100, meta_score=101, plot="Plot")


def test_invalid_plot_type():
    """
    Test creating a Movie instance with an invalid plot type.
    """
    with pytest.raises(AssertionError, match="plot must be a string"):
        Movie(movie_name="Test", rating=5.0, runtime=100, meta_score=80, plot=123)


def test_get_recommended_movies_returns_correct_amount(db_session):
    """
    Test that get_recommended_movies returns the correct number of movies.
    """
    # Create sample movies
    for i in range(15):
        db_session.add(Movie(
            movie_name=f"Movie {i}",
            rating=10 - i * 0.5,  # Decreasing rating
            runtime=120,
            meta_score=70,
            plot="Some plot"
        ))
    db_session.commit()

    # Request top 5 recommended
    recommended = Movie.get_recommended_movies_by_rating(db_session, amount=5)

    assert len(recommended) == 5
    assert all(isinstance(m, Movie) for m in recommended)
    assert recommended[0].rating > recommended[-1].rating  # Check descending order


def test_get_recommended_movies_defaults_to_10(db_session):
    """
    Test that get_recommended_movies defaults to returning 10 movies if no amount is specified.
    """
    # Create exactly 10 movies
    for i in range(10):
        db_session.add(Movie(
            movie_name=f"Film {i}",
            rating=0.5 + i,
            runtime=100,
            meta_score=60,
            plot="Plot"
        ))
    db_session.commit()

    # No amount specified → should return 10
    recommended = Movie.get_recommended_movies_by_rating(db_session)

    assert len(recommended) == 10


def test_get_recommended_movies_by_rating_returns_top_movies(db_session):
    """
    Test that get_recommended_movies_by_rating returns the top-rated movies.
    """
    # Arrange
    movie1 = Movie(rating=9.0, movie_name="Top Movie", runtime=120, meta_score=85, plot="A great movie")
    movie2 = Movie(rating=8.5, movie_name="Second Best", runtime=130, meta_score=80, plot="Another great movie")
    db_session.add(movie1)
    db_session.add(movie2)
    db_session.commit()

    # Act
    result = Movie.get_recommended_movies_by_rating(db_session, amount=2)

    # Assert
    assert result == [movie1, movie2]


def test_get_recommended_movies_by_friends_returns_sorted_unwatched(db_session):
    """
    Test that get_recommended_movies_by_friends returns unwatched movies
    sorted by how many friends watched them.
    """
    # Arrange
    movie1 = Movie(rating=7.0, movie_name="Movie 1", runtime=100, meta_score=70, plot="Plot 1")
    movie2 = Movie(rating=8.5, movie_name="Movie 2", runtime=110, meta_score=85, plot="Plot 2")
    movie3 = Movie(rating=6.5, movie_name="Movie 3", runtime=90, meta_score=60, plot="Plot 3")
    movie4 = Movie(rating=7.8, movie_name="Movie 4", runtime=105, meta_score=75, plot="Plot 4")
    movie5 = Movie(rating=7.2, movie_name="Movie 5", runtime=95, meta_score=65, plot="Plot 5")

    db_session.add_all([movie1, movie2, movie3, movie4, movie5])
    db_session.commit()

    friends_watched = {
        1: [1, 2, 3],
        2: [2, 3, 4],
        3: [2, 5]
    }
    self_watched = [3]

    # Act
    result = Movie.get_recommended_movies_by_friends(
        friends_watched=friends_watched,
        self_watched=self_watched,
        db_session=db_session,
        amount=3
    )

    assert [m.movie_id for m in result] == [2, 1, 4]


def test_get_recommended_movies_by_friends_returns_empty_if_all_watched(db_session):
    """
    Test that get_recommended_movies_by_friends returns an empty list
    if the user has already watched all the movies their friends have watched.
    """
    # Arrange
    movie1 = Movie(rating=7.0, movie_name="Movie 1", runtime=100, meta_score=70, plot="Plot 1")
    db_session.add(movie1)
    db_session.commit()

    friends_watched = {
        1: [1],
        2: [1]
    }
    self_watched = [1]

    # Act
    result = Movie.get_recommended_movies_by_friends(
        friends_watched=friends_watched,
        self_watched=self_watched,
        db_session=db_session,
        amount=2
    )

    # Assert
    assert result == []


@patch("src.database.models.movie.requests.get")
def test_get_poster_path_returns_correct_url(mock_get):
    """
    Test that get_poster_path returns the correct poster URL using mocked API response.
    """
    # Arrange
    movie = Movie(
        movie_name="Inception",
        rating=8.8,
        runtime=148,
        meta_score=74,
        plot="A thief steals corporate secrets using dream-sharing technology."
    )
    fake_response = {"results": [{"poster_path": "/inception.jpg"}]}

    mock_response = MagicMock()
    mock_response.json.return_value = fake_response
    mock_get.return_value = mock_response

    # Act
    result = movie.get_poster_path()

    # Assert
    assert result == "https://image.tmdb.org/t/p/w500/inception.jpg"
    mock_get.assert_called_once()
