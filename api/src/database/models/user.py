"""
This module defines the User model for the application.
"""
from hashlib import sha256
from sqlalchemy.orm import mapped_column, Mapped
from src.database.base import Base


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

    def __repr__(self) -> str:
        """
        Return a string representation of the User instance.
        :return: String representation of the User instance.
        """
        return f"<User {self.username}>"

    def __init__(self, username: str, password: str, is_active: bool = True, is_admin: bool = False):
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
        return sha256(password.encode()).hexdigest() == self.password
