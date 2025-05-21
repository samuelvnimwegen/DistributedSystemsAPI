"""
This script is used to consume the movie API and activity API.
"""
import logging

import requests

session = requests.Session()


def sign_up():
    """
    *** Functionality 1. Creating a user ***
    """
    logging.info("Testing functionality 1: Creating a user")
    assert session.cookies == {}
    response = session.post(
        "http://localhost/api/users/sign_up",
        json={
            "username": "testfriend",
            "password": "testpassword",
        }
    )
    assert response.status_code == 200, "Sign up failed"
    assert session.cookies != {}, "Session cookies are not set after sign up"
    assert "access_token_cookie" in session.cookies, "Access token cookie is not set"
    assert "csrf_access_token" in session.cookies, "CSRF access token cookie is not set"

    response = session.post(
        "http://localhost/api/users/sign_up",
        json={
            "username": "testuser",
            "password": "testpassword",
        }
    )
    assert response.status_code == 200, "Sign up failed"
    assert session.cookies != {}, "Session cookies are not set after sign up"
    assert "access_token_cookie" in session.cookies, "Access token cookie is not set"
    assert "csrf_access_token" in session.cookies, "CSRF access token cookie is not set"
    logging.info("Testing functionality 1: Creating a user passed")


def add_friend():
    """
    *** Functionality 2. Adding a friend ***
    """
    logging.info("Testing functionality 2: Adding a friend")
    assert session.cookies != {}, "Session cookies are not set before adding friend"
    response = session.post(
        "http://localhost/api/users/friends/testfriend",
        json={
            "friend_username": "testuser2",
        },
        headers={
            "X-CSRF-Token": session.cookies["csrf_access_token"],
        }
    )
    assert response.status_code == 200, "Add friend failed"

    response = session.get(
        "http://localhost/api/users/friends",
    )
    assert response.status_code == 200, "Add friend failed"
    assert len(response.json().get("results", [])) == 1, "Add friend failed"

    logging.info("Testing functionality 2: Adding a friend passed")


def watch_movie():
    """
    *** Functionality 3. Watching a movie ***
    """
    logging.info("Testing functionality 3: Watching a movie")
    assert session.cookies != {}, "Session cookies are not set before watching movie"
    response = session.post(
        "http://localhost/api/activity/watched/1",
        headers={
            "X-CSRF-Token": session.cookies["csrf_access_token"],
        }
    )
    assert response.status_code == 200, "Watch movie failed"

    response = session.get(
        "http://localhost/api/activity/watched/1",
    )
    assert response.status_code == 200, "Watch movie failed"
    assert response.json() == {"message": "Movie is watched."}
    logging.info("Testing functionality 4: Watching a movie passed")


def rate_movie():
    """
    *** Functionality 4. Rating a movie ***
    """
    logging.info("Testing functionality 4: Rating a movie")
    assert session.cookies != {}, "Session cookies are not set before rating movie"
    response = session.post(
        "http://localhost/api/preference/rating/1",
        params={
            "rating": 5,
            "movie_id": 1,
        },
        headers={
            "X-CSRF-Token": session.cookies["csrf_access_token"],
        }
    )
    assert response.status_code == 200, "Rate movie failed"

    response = session.get(
        "http://localhost/api/preference/rating/1",
        params={
            "movie_id": 1,
        },
        headers={
            "X-CSRF-Token": session.cookies["csrf_access_token"],
        }
    )
    assert response.status_code == 200, "Rate movie failed"
    assert len(response.json().get("results", [])) == 1, "Rate movie failed"
    logging.info("Functionality 4: Rating a movie passed")


def view_friends_rated_movies():
    """
    *** Functionality 5. Viewing friends' rated movies ***
    """
    logging.info("Testing functionality 5: Viewing friends' rated movies")
    # First we log in a the friend
    assert session.cookies != {}, "Session cookies are not set before viewing friends rated movies"
    response = session.post(
        "http://localhost/api/users/login",
        json={
            "username": "testfriend",
            "password": "testpassword",
        }
    )
    assert response.status_code == 200, "Login failed"
    assert session.cookies != {}, "Session cookies are not set after login"

    # We watch the movie with id 2
    response = session.post(
        "http://localhost/api/activity/watched/2",
        headers={
            "X-CSRF-Token": session.cookies["csrf_access_token"],
        }
    )
    assert response.status_code == 200, "Watch movie failed"

    # We now make a review on movie with id 2
    response = session.post(
        "http://localhost/api/preference/rating/2",
        json={
            "review": "This is a review",
            "rating": 5,
        },
        headers={
            "X-CSRF-Token": session.cookies["csrf_access_token"],
        }
    )
    assert response.status_code == 200, "Review movie failed"

    # Now we log in the user
    assert session.cookies != {}, "Session cookies are not set before viewing friends rated movies"
    response = session.post(
        "http://localhost/api/users/login",
        json={
            "username": "testuser",
            "password": "testpassword",
        }
    )
    assert response.status_code == 200, "Login failed"

    # Now we view the friends rated movies
    response = session.get(
        "http://localhost/api/preference/rating/friends",
        params={
            "friend_username": "testfriend",
        },
        headers={
            "X-CSRF-Token": session.cookies["csrf_access_token"],
        }
    )
    assert response.status_code == 200, "View friends rated movies failed"
    assert len(response.json().get("results", [])) == 1, "View friends rated movies failed"
    logging.info("Functionality 5: Viewing friends' rated movies passed")


def review_friends_rating():
    """
    *** Functionality 6. Reviewing a friend's rating ***
    """
    logging.info("Testing functionality 6: Reviewing a friend's rating")
    # We know the review id is 2 since it was the second review that was made in this script
    response = session.post(
        "http://localhost/api/preference/rating_review/2",
        json={
            "agreed": "True",
        },
        headers={
            "X-CSRF-Token": session.cookies["csrf_access_token"],
        }
    )
    assert response.status_code == 200, "Review friends rating failed"

    # Now get the value
    response = session.get(
        "http://localhost/api/preference/rating_review/2",
        headers={
            "X-CSRF-Token": session.cookies["csrf_access_token"],
        }
    )
    assert response.status_code == 200, "Review friends rating failed"
    assert len(response.json().get("results", [])) == 1, "Review friends rating failed"
    logging.info("Functionality 6: Reviewing a friend's rating passed")


def get_recommendations_rating():
    """
    *** Functionality 7. Getting recommendations based on ratings ***
    """
    logging.info("Testing functionality 7: Getting recommendations based on ratings")
    # We know the review id is 2 since it was the second review that was made in this script
    response = session.get(
        "http://localhost/api/preference/recommendations",
        params={
            "amount": 5,
        },
        headers={
            "X-CSRF-Token": session.cookies["csrf_access_token"],
        }
    )
    results = response.json().get("results", [])
    assert response.status_code == 200, "Get recommendations based on ratings failed"
    assert len(results) == 5, "Get recommendations based on ratings failed"
    assert results[0].get("rating") >= results[1].get("rating"), "Get recommendations based on ratings failed"
    assert results[1].get("rating") >= results[2].get("rating"), "Get recommendations based on ratings failed"
    assert results[2].get("rating") >= results[3].get("rating"), "Get recommendations based on ratings failed"
    assert results[3].get("rating") >= results[4].get("rating"), "Get recommendations based on ratings failed"
    logging.info("Functionality 7: Getting recommendations based on ratings passed")


def get_recommendations_friends_watched():
    """
    *** Functionality 8. Getting recommendations based on friends watched movies ***
    """
    logging.info("Testing functionality 8: Getting recommendations based on friends watched movies")
    response = session.get(
        "http://localhost/api/preference/recommendations/friends",
        params={
            "amount": 5,
        },
        headers={
            "X-CSRF-Token": session.cookies["csrf_access_token"],
        }
    )
    results = response.json().get("results", [])
    assert response.status_code == 200, "Get recommendations based on friends watched movies failed"

    # Since the friend has only watched one movie, we can only get one recommendation
    assert len(results) == 1, "Get recommendations based on friends watched movies failed"
    assert results[0].get("movie_id") == 2, "Get recommendations based on friends watched movies failed"
    logging.info("Functionality 8: Getting recommendations based on friends watched movies passed")


def get_newsfeed():
    """
    *** Functionality 9. Getting the newsfeed ***
    """
    logging.info("Testing functionality 9: Getting the newsfeed")
    response = session.get(
        "http://localhost/api/activity/newsfeed",
        headers={
            "X-CSRF-Token": session.cookies["csrf_access_token"],
        }
    )
    results = response.json().get("results", [])
    assert response.status_code == 200, "Get newsfeed failed"
    assert len(results) == 1, "Get newsfeed failed"
    assert results[0].get("movie_id") == 2, "Get newsfeed failed"
    logging.info("Functionality 9: Getting newsfeed passed")


def get_movie_list():
    """
    *** Functionality 10. Getting the movie list ***
    """
    logging.info("Testing functionality 10: Getting the movie list")
    response = session.get(
        "http://localhost/api/movies/list",
        headers={
            "X-CSRF-Token": session.cookies["csrf_access_token"],
        },
        params={
            "amount": 20,
        }
    )
    results = response.json().get("results", [])
    assert response.status_code == 200, "Get movie list failed"
    assert len(results) == 20, "Get movie list failed"
    logging.info("Functionality 10: Getting movie list passed")


if __name__ == "__main__":
    sign_up()
    add_friend()
    watch_movie()
    rate_movie()
    view_friends_rated_movies()
    review_friends_rating()
    get_recommendations_rating()
    get_recommendations_friends_watched()
    get_newsfeed()
    get_movie_list()
    logging.info("All tests passed")
