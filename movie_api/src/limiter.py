"""
This module sets up the Flask-Limiter for the application.

This is the default configuration for the Flask-Limiter.
Every user is limited to 200 requests per day and 50 requests per hour.
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    get_remote_address,
    default_limits=["1000 per day", "200 per hour"],
    storage_uri="memory://",
)
