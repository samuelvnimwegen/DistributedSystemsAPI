"""
Test cases for the Genre model in the database.
"""
from src.database.models.genre import Genre
from src.database.models.movie import Movie


def test_create_genre():
    """
    Test creating a valid Genre instance.
    """
    genre = Genre(genre_name="Action")
    assert genre.genre_name == "Action"
    assert isinstance(genre.movies, list)


def test_genre_movie_association(db_session):
    """
    Test the association between Genre and Movie.
    """
    genre = Genre(genre_name="Sci-Fi")
    movie = Movie(movie_name="Interstellar", rating=8.6, runtime=169, meta_score=74, plot="A space epic.")

    genre.movies.append(movie)
    db_session.add(genre)
    db_session.commit()

    fetched_genre = db_session.query(Genre).filter_by(genre_name="Sci-Fi").first()
    assert fetched_genre is not None
    assert len(fetched_genre.movies) == 1
    assert fetched_genre.movies[0].movie_name == "Interstellar"


def test_get_genre_when_exists(db_session):
    """
    Test getting a Genre object when it already exists in the database.
    """
    genre = Genre(genre_name="Thriller")
    db_session.add(genre)
    db_session.commit()

    fetched = Genre.get_genre("Thriller", db_session)
    assert fetched.genre_name == "Thriller"
    assert fetched.genre_id == genre.genre_id  # Should be the same instance from DB


def test_get_genre_when_not_exists(db_session):
    """
    Test getting a Genre object when it does not exist in the database.
    """
    fetched = Genre.get_genre("Fantasy", db_session)
    assert fetched is not None
    assert fetched.genre_name == "Fantasy"
    assert fetched.genre_id is not None

    # Check if it was actually added to the DB
    persisted = db_session.query(Genre).filter_by(genre_name="Fantasy").first()
    assert persisted is not None
    assert persisted.genre_id == fetched.genre_id
