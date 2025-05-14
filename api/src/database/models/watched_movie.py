
from typing import TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from src.database.base import Base

if TYPE_CHECKING:
    from src.database.models import User, Movie

class WatchedMovie(Base):
    """
    WatchedMovie model for the application, representing a many-to-many relationship
    """
    __tablename__ = "watched_movie"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    """The ID of the user who watched the movie."""

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.movie_id"), primary_key=True)
    """The ID of the movie that was watched."""

    watched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    """The date and time when the movie was watched."""

    user: Mapped["User"] = relationship("User", back_populates="watched_movie_associations", overlaps="watched_movies,users_watched")
    """The user who watched the movie."""

    movie: Mapped["Movie"] = relationship("Movie", back_populates="watched_movie_associations", overlaps="watched_movies,users_watched")
    """The movie that was watched."""
