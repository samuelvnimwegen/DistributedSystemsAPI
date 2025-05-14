"""
This module contains the Movie model for the database.
"""
from typing import TYPE_CHECKING, Optional
from collections import Counter
from sqlalchemy.orm import relationship, mapped_column, Mapped, Session
from sqlalchemy import Table, Column, ForeignKey
from src.database.base import Base

if TYPE_CHECKING:
    from src.database.models import Genre, Rating, User, WatchedMovie

movie_genre_association = Table(
    "has_genre",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.movie_id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.genre_id"), primary_key=True),
)

class Movie(Base):
    """
    Movie model for the database.
    """
    __tablename__ = "movies"

    movie_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """The unique identifier for the movie."""

    movie_name: Mapped[str]
    """The name of the movie."""

    rating: Mapped[float]
    """The rating of the movie."""

    runtime: Mapped[int]
    """The runtime of the movie in minutes."""

    genres: Mapped[list["Genre"]] = relationship(secondary=movie_genre_association, back_populates="movies")
    """The list of genres associated with the movie."""

    meta_score: Mapped[Optional[int]]
    """The meta score of the movie."""

    plot: Mapped[str]
    """The plot of the movie."""

    ratings: Mapped[list["Rating"]] = relationship(back_populates="movie")
    """The list of ratings associated with the movie."""

    users_watched: Mapped[list["User"]] = relationship(
        "User",
        secondary="watched_movie",
        back_populates="watched_movies"
    )
    """The list of users who have watched the movie."""

    watched_movie_associations: Mapped[list["WatchedMovie"]] = relationship(
        back_populates="movie", overlaps="users_watched,watched_movies"
    )
    """The list of watched movie associations."""

    def __init__(
        self,
        movie_name: str,
        rating: float,
        runtime: int,
        plot: str,
        meta_score: Optional[int] = None
    ) -> None:
        """
        Initialize a Movie object.
        :param movie_name: The name of the movie.
        :param rating: The rating of the movie.
        :param runtime: The runtime of the movie in minutes.
        :param meta_score: The meta score of the movie.
        :param plot: The plot of the movie.
        """
        assert isinstance(movie_name, str), "movie_name must be a string"
        assert isinstance(rating, (int, float)), "rating must be a number"
        assert isinstance(runtime, int), "runtime must be an integer"
        assert isinstance(meta_score, int), "meta_score must be an integer"
        assert isinstance(plot, str), "plot must be a string"
        assert rating >= 0, "rating must be non-negative"
        assert runtime > 0, "runtime must be positive"
        assert meta_score >= 0 or meta_score is None, "meta_score must be non-negative"
        assert meta_score <= 100 or meta_score is None, "meta_score must be less than or equal to 100"
        assert len(movie_name) > 0, "movie_name must not be empty"
        assert len(plot) > 0, "plot must not be empty"
        assert runtime <= 300, "runtime must be less than or equal to 300 minutes"
        assert rating <= 10, "rating must be less than or equal to 10"

        super().__init__()
        self.movie_name = movie_name
        self.rating = rating
        self.runtime = runtime
        self.meta_score = meta_score
        self.plot = plot

    def __repr__(self) -> str:
        """
        String representation of the Movie object.
        :return: String representation of the Movie object.
        """
        return (f"<Movie(movie_id={self.movie_id}, movie_name='{self.movie_name}', rating={self.rating}, "
                f"runtime={self.runtime})>")

    @staticmethod
    def get_recommended_movies_by_rating(db_session: Session, amount: int = 10) -> list["Movie"]:
        """
        Get recommended movies based on the average rating of all movies.
        :param db_session: The database session.
        :param amount: The number of recommended movies to return.
        :return: List of recommended movies.
        """
        recommended_movies = db_session.query(Movie).order_by(Movie.rating.desc()).limit(amount).all()
        return recommended_movies

    @staticmethod
    def get_recommended_movies_by_friends(user: "User", db_session: Session, amount: int = 10) -> list["Movie"]:
        """
        Get recommended movies based on which movies friends have watched.
        :param user: The User instance.
        :param db_session: The database session.
        :param amount: The number of recommended movies to return.
        :return: List of recommended movies.
        """
        friends = user.get_friends()

        # Get movie_ids watched by friends
        movie_counter: Counter[int] = Counter()

        for friend in friends:
            movie_counter.update(movie.movie_id for movie in friend.watched_movies)

        # Exclude movies already watched by the user
        watched_movie_ids = {movie.movie_id for movie in user.watched_movies}
        candidate_ids = [movie_id for movie_id, _ in movie_counter.most_common() if movie_id not in watched_movie_ids]

        if not candidate_ids:
            return []

        result_amount = min(amount, len(candidate_ids))

        # Query top N recommended movies in a single query
        recommended_movies = (
            db_session.query(Movie)
            .filter(Movie.movie_id.in_(candidate_ids))
            .all()
        )

        # Maintain ordering based on friend popularity
        recommended_movies.sort(key=lambda m: movie_counter[m.movie_id], reverse=True)

        return recommended_movies[:result_amount]
