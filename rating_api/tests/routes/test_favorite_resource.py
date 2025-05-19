"""
This module contains tests for the favorite resource routes.
"""
from src.database import FavoriteMovie


def test_add_movie_to_favorites(client, db_session):
    """
    Test adding a movie to the favorites list.
    """
    movie_id = 123
    response = client.post(f"/api/preference/favorite/{movie_id}", headers={"X-CSRF-Token": client.csrf_token})

    assert response.status_code == 200
    assert response.json["message"] == "Movie added to favorites."

    # Check in DB
    fav = db_session.query(FavoriteMovie).filter_by(user_id=1, movie_id=movie_id).first()
    assert fav is not None


def test_add_duplicate_favorite(client, db_session):
    """
    Test adding a duplicate movie to the favorites list.
    """
    movie_id = 123
    db_session.add(FavoriteMovie(user_id=1, movie_id=movie_id))
    db_session.commit()

    response = client.post(f"/api/preference/favorite/{movie_id}", headers={"X-CSRF-Token": client.csrf_token})
    assert response.status_code == 200
    assert response.json["message"] == "Movie already in favorites."


def test_get_favorite_status_true(client, db_session):
    """
    Test getting the favorite status of a movie.
    """
    movie_id = 123
    db_session.add(FavoriteMovie(user_id=1, movie_id=movie_id))
    db_session.commit()

    response = client.get(f"/api/preference/favorite/{movie_id}", headers={"X-CSRF-Token": client.csrf_token})
    assert response.status_code == 200
    assert response.json["message"] == "Movie is a favorite."


def test_get_favorite_status_false(client):
    """
    Test getting the favorite status of a movie that is not a favorite.
    """
    response = client.get("/api/preference/favorite/999")
    assert response.status_code == 200
    assert response.json["message"] == "Movie is not in the favorite list."


def test_delete_favorite_existing(client, db_session):
    """
    Test deleting a movie from the favorites list.
    """
    movie_id = 123
    db_session.add(FavoriteMovie(user_id=1, movie_id=movie_id))
    db_session.commit()

    response = client.delete(f"/api/preference/favorite/{movie_id}", headers={"X-CSRF-Token": client.csrf_token})
    assert response.status_code == 200
    assert response.json["message"] == "Movie removed from favorites."

    # Check removal
    assert not db_session.query(FavoriteMovie).filter_by(user_id=1, movie_id=movie_id).first()


def test_delete_favorite_nonexistent(client):
    """
    Test deleting a movie that is not in the favorites list.
    """
    response = client.delete("/api/preference/favorite/999", headers={"X-CSRF-Token": client.csrf_token})
    assert response.status_code == 200
    assert response.json["message"] == "Movie not in favorites."
