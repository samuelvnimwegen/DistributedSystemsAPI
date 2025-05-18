"""
Rating model for the database.
"""
from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship, mapped_column, Mapped
from src.database.base import Base

if TYPE_CHECKING:
    from src.database.models import User, Movie, RatingReview


class Rating(Base):
    """
    Rating model for the database.
    """
    __tablename__ = "ratings"

    rating_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """The unique identifier for the rating."""

    rating: Mapped[float]
    """The rating value."""

    user_id: Mapped[int]
    """The ID of the user who made the rating."""

    movie_id: Mapped[int]
    """The ID of the movie being rated."""

    rating_reviews: Mapped["RatingReview"] = relationship(back_populates="rating")
    """The list of approvals associated with the rating."""

    def __init__(
        self,
        rating: float,
        user_id: int,
        movie_id: int,
    ) -> None:
        """
        Initialize a Rating object.
        :param rating: The rating value.
        :param user_id: The ID of the user who made the rating.
        :param movie_id: The ID of the movie being rated.
        """
        assert isinstance(rating, (float, int)), "Rating must be a float."
        assert isinstance(user_id, int), "User ID must be an integer."
        assert isinstance(movie_id, int), "Movie ID must be an integer."
        assert rating > 0, "Rating must be greater than 0."
        assert rating <= 10, "Rating must be less than or equal to 10."
        assert user_id > 0, "User ID must be greater than 0."
        assert movie_id > 0, "Movie ID must be greater than 0."
        super().__init__()
        self.rating = rating
        self.user_id = user_id
        self.movie_id = movie_id

    def __repr__(self) -> str:
        """
        Return a string representation of the Rating object.
        :return: String representation of the Rating object.
        """
        return (f"Rating(rating_id={self.rating_id}, rating={self.rating}, "
                f"user_id={self.user_id}, movie_id={self.movie_id})")
