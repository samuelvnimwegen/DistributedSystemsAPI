from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from src.database.base import Base


class WatchedMovie(Base):
    """
    WatchedMovie model for the application, representing a many-to-many relationship
    """
    __tablename__ = "watched_movie"

    watched_movie_id: Mapped[int] = mapped_column(primary_key=True)
    """The ID of the watched movie entry."""

    user_id: Mapped[int]
    """The ID of the user who watched the movie."""

    movie_id: Mapped[int]
    """The ID of the movie that was watched."""

    watched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    """The date and time when the movie was watched."""
