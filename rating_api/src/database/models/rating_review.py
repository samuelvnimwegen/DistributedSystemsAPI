"""
This module defines the Rating Review model for the application.
"""
from typing import TYPE_CHECKING
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey
from src.database.base import Base

if TYPE_CHECKING:
    from src.database.models import Rating


class RatingReview(Base):
    """
    RatingReview model for the application, whether a rating is approved or not by another user.
    """
    __tablename__ = "rating_reviews"

    rating_review_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """The unique identifier for the rating review."""

    user_id: Mapped[int]
    """The ID of the user who made the rating review."""

    rating_id: Mapped[int] = mapped_column(ForeignKey("ratings.rating_id"))
    """The ID of the movie being approved."""

    rating: Mapped["Rating"] = relationship(back_populates="rating_reviews")
    """The rating being approved."""

    agreed: Mapped[bool]
    """Indicates if the rating review is agreed or not."""

    def __init__(self, user_id: int, rating_id: int, agreed: bool) -> None:
        """
        Initialize a RatingReview object.
        :param user_id: The ID of the user who made the rating review.
        :param rating_id: The ID of the movie being approved.
        :param agreed: Indicates if the rating review is agreed or not.
        """
        assert isinstance(user_id, int), "User ID must be an integer."
        assert isinstance(rating_id, int), "Rating ID must be an integer."
        assert isinstance(agreed, bool), "Agreed must be a boolean."
        assert user_id > 0, "User ID must be greater than 0."
        assert rating_id > 0, "Rating ID must be greater than 0."
        super().__init__()

        self.user_id = user_id
        self.rating_id = rating_id
        self.agreed = agreed
