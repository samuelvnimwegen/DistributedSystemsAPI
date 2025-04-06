"""
This module contains fixtures for setting up the test environment.
The fixtures are used to create a test database and provide an SQLAlchemy session for the tests.

Disclaimer: This is based on our bachelor eindwerk project setup, which I also largely contributed to.
"""
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor
import pytest
from sqlalchemy import text
from src.config import APIConfig, LoggingConfig, DBConfig, LogLevel
from src.app import create_app
from src.database import db

test_db = factories.postgresql_proc(port=None, dbname="test_db")


# pylint: disable=redefined-outer-name

@pytest.fixture(scope="session")
def app(test_db):
    """
    This fixture returns a Flask app with an in-memory SQLite database.
    """
    pg_host = test_db.host
    pg_port = test_db.port
    pg_user = test_db.user
    pg_db = test_db.dbname
    pg_password = test_db.password

    with DatabaseJanitor(
        user=pg_user,
        host=pg_host,
        port=pg_port,
        dbname=pg_db,
        version=test_db.version,
        password=pg_password
    ):
        config = APIConfig(
            name="test_api",
            db=DBConfig(connection_url=f"postgresql+psycopg://{pg_user}:@{pg_host}:{pg_port}/{pg_db}"),
            logging=LoggingConfig(level=LogLevel.DEBUG),
            debug=True
        )
        app = create_app(config)

        app.config['JWT_ALGORITHM'] = 'HS256'
        app.config['JWT_SECRET_KEY'] = app.config['SECRET_KEY']
        app.config['JWT_COOKIE_NAME'] = 'access_token_cookie'

        with app.app_context():
            db.create_all()
            yield app


@pytest.fixture(scope="function")
def db_session(app):  # pylint: disable=unused-argument
    """
    This fixture returns a SQLAlchemy session for the tests.
    """
    with db.engine.connect() as connection:
        transaction = connection.begin()

        yield db.session
        db.session.rollback()
        transaction.rollback()

        connection.execute(text("SET session_replication_role = 'replica';"))

        # truncate all tables to remove data and reset primary key sequences
        # this makes the tests independent of each other
        for table in reversed(db.metadata.sorted_tables):
            connection.execute(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE;'))

        # re-enable foreign key constraints
        connection.execute(text("SET session_replication_role = 'origin';"))
        connection.commit()

        # extra check to make sure all tables are empty
        for table in reversed(db.metadata.sorted_tables):
            assert len(connection.execute(table.select()).fetchall()) == 0


@pytest.fixture(scope="function")
def client(app, db_session):  # pylint: disable=unused-argument
    """
    Return a Flask test client for making requests.
    """
    with app.test_client() as client:
        return client
