"""
The table for the favorite movies of the users.
"""
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.database.base import Base


class FavoriteMovie(Base):
    """
    FavoriteMovie model for the database.
    """
    __tablename__ = "favorite_movies"

    favorite_movie_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """The unique identifier for the favorite movie."""

    user_id: Mapped[int] = mapped_column()
    """The ID of the user who made the rating."""

    movie_id: Mapped[int] = mapped_column()
    """The ID of the movie being rated."""

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="unique_favorite_movie"),
    )

    def __init__(self, user_id: int, movie_id: int) -> None:
        """
        Initialize a FavoriteMovie object.
        :param user_id: The ID of the user who made the rating.
        :param movie_id: The ID of the movie being rated.
        """
        assert isinstance(user_id, int), "User ID must be an integer."
        assert isinstance(movie_id, int), "Movie ID must be an integer."
        assert user_id > 0, "User ID must be greater than 0."
        assert movie_id > 0, "Movie ID must be greater than 0."
        super().__init__()

        self.user_id = user_id
        self.movie_id = movie_id

    def __repr__(self) -> str:
        """
        Return a string representation of the Favorite Movie object.
        :return: String representation of the Favorite Movie object.
        """
        return f"FavoriteMovie(user_id={self.user_id}, movie_id={self.movie_id})"
