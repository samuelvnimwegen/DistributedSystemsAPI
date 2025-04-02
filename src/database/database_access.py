"""
This module contains the database access class that contains all the access methods
"""
from sqlalchemy.orm import scoped_session
from src.database.database import db as _db


# pylint: disable=too-few-public-methods

class DatabaseAccess:
    """
    This is the general database access class that contains all the access methods
    for the database.
    """

    def __init__(self, session: scoped_session = _db.session):
        """
        Initializes the database access class.
        Please add all the access methods here.
        """
        self.session = session
