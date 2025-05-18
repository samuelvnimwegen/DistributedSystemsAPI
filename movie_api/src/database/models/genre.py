"""
This module defines the Genre model for the application.
"""

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.orm import Session

from src.database.base import Base
from src.database.models.movie import Movie, movie_genre_association


class Genre(Base):
    """
    Genre model for the application.
    """
    __tablename__ = "genres"

    genre_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """The unique identifier for the genre."""

    genre_name: Mapped[str]
    """The name of the genre."""

    movies: Mapped[list["Movie"]] = relationship(
        secondary=movie_genre_association,
        back_populates="genres"
    )
    """The list of movies associated with the genre."""

    @staticmethod
    def get_genre(genre_name: str, db_session: Session) -> "Genre":
        """
        Get the Genre object based on the genre name.
        :param genre_name: The name of the genre.
        :param db_session: The database session.
        :return: The Genre object.
        """
        genre = db_session.query(Genre).filter(Genre.genre_name == genre_name).first()
        if genre is None:
            genre = Genre(genre_name=genre_name)
            db_session.add(genre)
            db_session.commit()
        return genre
