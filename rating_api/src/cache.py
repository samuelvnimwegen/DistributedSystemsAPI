"""
Cache configuration for Flask application.

This module sets up the Flask-Caching for the application.
The default configuration is a simple cache with a timeout of 300 seconds (5 minutes).
"""
from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300
})
