"""
This file contains tests for the Movie model in the database.
"""
import pytest
from src.database.models import Movie, Genre, User


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


def test_no_friends_returns_empty(db_session):
    """
    Test that get_recommended_movies_by_friends returns an empty list if the user has no friends.
    """
    user = User(username="loner", password="test")
    db_session.add(user)
    db_session.commit()

    result = Movie.get_recommended_movies_by_friends(user, db_session)
    assert result == []


def test_friends_watched_movies_recommendation(db_session):
    """
    Test that get_recommended_movies_by_friends returns movies watched by friends.
    """
    # Create user and two friends
    user = User(username="main", password="test")
    friend1 = User(username="f1", password="test")
    friend2 = User(username="f2", password="test")

    movie1 = Movie(movie_name="Inception", rating=9.0, runtime=148, meta_score=74, plot="A mind-bending thriller.")
    movie2 = Movie(movie_name="Interstellar", rating=8.6, runtime=169, meta_score=74, plot="A space epic.")
    movie3 = Movie(
        movie_name="The Matrix",
        rating=8.7,
        runtime=136,
        meta_score=73,
        plot="A computer hacker learns about the true nature of reality."
    )

    db_session.add_all([user, friend1, friend2, movie1, movie2, movie3])
    db_session.commit()

    # Simulate friendships
    user.get_friends = lambda: [friend1, friend2]

    # Simulate watched movies
    friend1.watched_movies = [movie1, movie2]
    friend2.watched_movies = [movie1, movie3]
    user.watched_movies = [movie3]  # already watched movie3

    db_session.commit()

    result = Movie.get_recommended_movies_by_friends(user, db_session)

    # movie1 should appear first (watched by 2 friends), movie2 second
    assert len(result) == 2
    assert result[0].movie_name == "Inception"
    assert result[1].movie_name == "Interstellar"


def test_limit_amount_of_recommendations(db_session):
    """
    Test that get_recommended_movies_by_friends limits the number of recommendations to the specified amount.
    """
    user = User(username="main2", password="test")
    friend = User(username="friend", password="test")

    movies = [
        Movie(movie_name=f"Movie {i}", rating=2.0 + i, runtime=100 + i, meta_score=60 + i, plot="Plot")
        for i in range(1, 6)
    ]

    db_session.add_all([user, friend] + movies)
    db_session.commit()

    user.get_friends = lambda: [friend]
    friend.watched_movies = movies
    user.watched_movies = []

    result = Movie.get_recommended_movies_by_friends(user, db_session, amount=3)

    assert len(result) == 3
    # Order should be based on friend frequency (all equal here), so any 3 valid movies
    assert all(movie in movies for movie in result)
