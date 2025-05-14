"""
This module defines the User model for the application.
"""
from typing import TYPE_CHECKING
from hashlib import sha256
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Table, Column, ForeignKey

from src.database.base import Base

# pylint: disable=protected-access

friends_with_association = Table(
    "friends_with",
    Base.metadata,
    Column("user1_id", ForeignKey("users.user_id")),
    Column("user2_id", ForeignKey("users.user_id")),
)

if TYPE_CHECKING:
    from src.database.models import Rating, RatingReview, Movie, WatchedMovie


class User(Base):
    """
    User model for the application.
    """
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """The unique identifier for the user."""

    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    """The username of the user."""

    password: Mapped[str] = mapped_column(nullable=False)
    """The hashed password of the user."""

    is_active: Mapped[bool] = mapped_column(default=True)
    """Indicates if the user is active."""

    is_admin: Mapped[bool] = mapped_column(default=False)
    """Indicates if the user is an admin."""

    _friends: Mapped[list["User"]] = relationship(
        "User",
        secondary=friends_with_association,
        primaryjoin=(user_id == friends_with_association.c.user1_id),
        secondaryjoin=(user_id == friends_with_association.c.user2_id),
    )
    """The list of friends associated with the user."""

    ratings: Mapped[list["Rating"]] = relationship(back_populates="user")
    """The list of ratings associated with the user."""

    rating_reviews: Mapped[list["RatingReview"]] = relationship(back_populates="user")
    """The list of rating reviews associated with the user."""

    watched_movies: Mapped[list["Movie"]] = relationship(
        secondary="watched_movie",
        back_populates="users_watched",
    )
    """The list of movies watched by the user."""

    watched_movie_associations: Mapped[list["WatchedMovie"]] = relationship(
        back_populates="user", overlaps="users_watched,watched_movies"
    )
    """The list of watched movie associations for the user."""

    def get_friends(self) -> list["User"]:
        """
        Get the list of friends associated with the user.
        :return: List of friends.
        """
        return self._friends

    def add_friend(self, friend: "User") -> None:
        """
        Add a friend to the user.
        :param friend: The User instance to add as a friend.
        """
        assert isinstance(friend, User), "friend must be a User instance"
        assert friend.user_id != self.user_id, "Cannot add oneself as a friend"
        self._friends.append(friend)
        friend._friends.append(self)

    def remove_friend(self, friend: "User") -> None:
        """
        Remove a friend from the user.
        :param friend: The User instance to remove from friends.
        """
        assert isinstance(friend, User), "friend must be a User instance"
        assert friend.user_id != self.user_id, "Cannot remove oneself as a friend"
        self._friends.remove(friend)
        friend._friends.remove(self)

    def __repr__(self) -> str:
        """
        Return a string representation of the User instance.
        :return: String representation of the User instance.
        """
        return f"<User {self.username}>"

    def __init__(self, username: str, password: str, is_active: bool = True, is_admin: bool = False) -> None:
        """
        Initialize a new User instance.

        :param username: The username of the user.
        :param password: The hashed password of the user.
        """
        super().__init__()
        assert isinstance(username, str), "Username must be a string"
        assert isinstance(password, str), "Password must be a string"
        assert len(username) > 0, "Username cannot be empty"
        assert len(password) > 0, "Password cannot be empty"
        assert len(username) <= 50, "Username cannot exceed 50 characters"
        assert len(password) <= 255, "Password cannot exceed 255 characters"
        assert isinstance(is_active, bool), "is_active must be a boolean"
        assert isinstance(is_admin, bool), "is_admin must be a boolean"

        self.username = username
        self.password: str = sha256(password.encode()).hexdigest()
        self.is_active = is_active
        self.is_admin = is_admin

    def check_password(self, password: str) -> bool:
        """
        Check if the provided password matches the stored hashed password.

        :param password: The password to check.
        :return: True if the passwords match, False otherwise.
        """
        return bool(sha256(password.encode()).hexdigest() == self.password)

    def get_latest_watched_by_friends(self, amount: int = 10) -> list["WatchedMovie"]:
        """
        Get the latest watched movies by friends.
        """
        # Get all watched movies by friends
        friends = self.get_friends()
        associations: list["WatchedMovie"] = []
        for friend in friends:
            associations.extend(friend.watched_movie_associations)

        # Sort by watched_at date
        associations.sort(key=lambda m: m.watched_at, reverse=True)

        # Limit to the specified amount
        return associations[:amount]
