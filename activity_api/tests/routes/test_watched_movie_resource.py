"""
This file contains the test cases for the WatchedMovieResource class.
"""
from datetime import datetime, timedelta

from src.database import WatchedMovie


def test_mark_movie_as_watched(client, db_session):
    """
    Test marking a movie as watched.
    """
    headers = {
        "X-CSRF-Token": client.csrf_token,
    }
    response = client.post("/api/activity/watched/42", headers=headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Movie marked as watched"

    watched = db_session.query(WatchedMovie).filter_by(movie_id=42).first()
    assert watched is not None


def test_get_watched_movies(client, db_session):
    """
    Test getting watched movies for a user.
    """
    # Arrange
    db_session.add(WatchedMovie(user_id=1, movie_id=10))
    db_session.add(WatchedMovie(user_id=1, movie_id=11))
    db_session.commit()

    response = client.get("api/activity/watched/")
    assert response.status_code == 200
    data = response.get_json()
    assert "results" in data
    assert len(data["results"]) == 2


def test_get_filtered_watched_movies(client, db_session):
    """
    Test getting filtered watched movies for a user.
    """
    db_session.add(WatchedMovie(user_id=1, movie_id=10))
    db_session.add(WatchedMovie(user_id=2, movie_id=11))
    db_session.commit()

    response = client.get("/api/activity/watched/?user_id=2&movie_id=11")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["results"]) == 1
    assert data["results"][0]["user_id"] == 2


def test_get_watched_movies_since_timestamp(client, db_session):
    """
    Test getting watched movies since a specific timestamp.
    """

    past = datetime.now() - timedelta(days=2)
    recent = datetime.now() - timedelta(hours=1)

    db_session.add(WatchedMovie(user_id=1, movie_id=10, watched_at=past))
    db_session.add(WatchedMovie(user_id=1, movie_id=11, watched_at=recent))
    db_session.commit()

    since = (datetime.now() - timedelta(hours=2)).isoformat()
    response = client.get(f"/api/activity/watched/?since_timestamp={since}")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data["results"]) == 1
    assert data["results"][0]["movie_id"] == 11
