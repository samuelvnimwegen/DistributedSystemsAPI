"""
This script will consume the API and print the response.
"""
import requests
from PIL import Image
from io import BytesIO
from PIL import UnidentifiedImageError

BASE_URL = "http://localhost:5000"

session = requests.Session()
CSFR_headers = {}

def assert_correct_film_list(response) -> None:
    """
    Assert that the response is a correct film list.
    :param response: The response to check
    :return: None
    """
    assert response.status_code == 200
    assert "results" in response.json()
    assert isinstance(response.json()["results"], list)
    assert len(response.json()["results"]) > 0


def get_popular_amount():
    """
    Test the route /api/movies with different amounts.
    """
    print("Testing /api/movies route with different amounts")
    # Test with invalid amounts
    response = session.get(f"{BASE_URL}/api/movies?amount=21")
    assert response.status_code == 400
    assert response.json() == {"message": "Maximum amount allowed amount is 20."}

    response = session.get(f"{BASE_URL}/api/movies?amount=0")
    assert response.status_code == 400
    assert response.json() == {"message": "Minimum amount allowed amount is 1."}

    # Test with valid amounts
    response = session.get(f"{BASE_URL}/api/movies?amount=1")
    assert response.status_code == 200
    assert "results" in response.json()
    assert isinstance(response.json()["results"], list)
    assert len(response.json()["results"]) == 1

    response = session.get(f"{BASE_URL}/api/movies?amount=5")
    assert response.status_code == 200
    assert "results" in response.json()
    assert isinstance(response.json()["results"], list)
    assert len(response.json()["results"]) == 5

    response = session.get(f"{BASE_URL}/api/movies?amount=20")
    assert response.status_code == 200
    assert "results" in response.json()
    assert isinstance(response.json()["results"], list)
    assert len(response.json()["results"]) == 20

    # No amount specified
    response = session.get(f"{BASE_URL}/api/movies")
    assert response.status_code == 200
    assert "results" in response.json()
    assert isinstance(response.json()["results"], list)
    assert len(response.json()["results"]) == 1


def get_popular_content():
    """
    Test the /api/movies route for valid content.
    """
    print("Testing /api/movies route for valid content")
    response = session.get(f"{BASE_URL}/api/movies?amount=1")
    assert response.status_code == 200
    assert "results" in response.json()
    assert isinstance(response.json()["results"], list)
    assert len(response.json()["results"]) == 1

    movie = response.json()["results"][0]
    assert "id" in movie
    assert "title" in movie
    assert "overview" in movie
    assert "release_date" in movie
    assert "poster_path" in movie
    assert "popularity" in movie
    assert "vote_average" in movie
    assert "vote_count" in movie
    assert "backdrop_path" in movie
    assert "adult" in movie
    assert "genre_ids" in movie
    assert isinstance(movie["genre_ids"], list)
    assert all(isinstance(genre_id, int) for genre_id in movie["genre_ids"])
    assert isinstance(movie["id"], int)
    assert isinstance(movie["title"], str)
    assert isinstance(movie["overview"], str)
    assert isinstance(movie["release_date"], str)
    assert isinstance(movie["poster_path"], str)
    assert isinstance(movie["popularity"], float)
    assert isinstance(movie["vote_average"], float)
    assert isinstance(movie["vote_count"], int)
    assert isinstance(movie["backdrop_path"], str)


def get_same_genres_related_movie():
    """
    Test the /api/movies/same_genres route with a related movie.
    """
    print("Testing /api/movies/same_genres route with a related movie")
    # Test with invalid movie_id
    response = session.get(f"{BASE_URL}/api/movies/{0}/same_genres")
    assert response.status_code == 404

    # Test with ID of a popular movie (the Minecraft movie)
    mc_movie_id = 950387
    response = session.get(f"{BASE_URL}/api/movies/{mc_movie_id}/same_genres")
    assert response.status_code == 200

    # See that the movie with the title "Shrek" is in the list of related movies
    assert_correct_film_list(response)
    assert any(movie["title"] == "Shrek" for movie in response.json()["results"])


def get_same_genres_no_related_movie():
    """
    Test the /api/movies/same_genres route with a movie that has no related movies.
    """
    print("Testing /api/movies/same_genres route with a movie that has no related movies")
    # Test with ID of a movie that Shrek is not related to (Captain America: Brave New World)
    cap_america_id = 822119
    response = session.get(f"{BASE_URL}/api/movies/{cap_america_id}/same_genres")
    assert response.status_code == 200

    # See that the movie with the title "Shrek" is not in the list of related movies
    assert_correct_film_list(response)
    assert not any(movie["title"] == "Shrek" for movie in response.json()["results"])


def get_same_genres_movie_itself_excluded():
    """
    Test the /api/movies/same_genres route to see whether the movie that is queried is not in the results.
    """
    print("Testing /api/movies/same_genres route to see whether the movie that is queried is not in the results")
    # Test with ID of a popular movie (the Minecraft movie)
    mc_movie_id = 950387
    response = session.get(f"{BASE_URL}/api/movies/{mc_movie_id}/same_genres")
    assert response.status_code == 200

    # See that the movie with the title "Shrek" is not in the list of related movies
    assert_correct_film_list(response)
    assert not any(movie["title"] == "A Minecraft Movie" for movie in response.json()["results"])


def get_similar_runtime_similar():
    """
    Test the /api/movies/similar_runtime route with a movie that has similar runtime.
    """
    print("Testing /api/movies/similar_runtime route with a movie that has similar runtime")
    # Test with ID of a popular movie (the Minecraft movie)
    mc_movie_id = 950387
    response = session.get(f"{BASE_URL}/api/movies/{mc_movie_id}/similar_runtime")
    assert_correct_film_list(response)


def get_similar_runtime_not_similar():
    """
    Test the /similar_runtime route with a movie that has not similar runtime.
    """
    print("Testing /api/movies/similar_runtime route with a movie that has not similar runtime")
    # Test with ID of a popular movie (the Minecraft movie)
    mc_movie_id = 950387
    response = session.get(f"{BASE_URL}/api/movies/{mc_movie_id}/similar_runtime")
    assert_correct_film_list(response)
    assert not any(movie["title"] == "Interstellar" for movie in response.json()["results"])


def get_similar_runtime_movie_itself_excluded():
    """
    Test the /similar_runtime route to see whether the movie that is queried is not in the results.
    """
    print("Testing /api/movies/similar_runtime route to see whether the movie that is queried is not in the results")
    # Test with ID of a popular movie (the Minecraft movie)
    mc_movie_id = 950387
    response = session.get(f"{BASE_URL}/api/movies/{mc_movie_id}/similar_runtime")
    assert_correct_film_list(response)
    assert not any(movie["title"] == "A Minecraft Movie" for movie in response.json()["results"])


def get_score_plot():
    """
    Test the /api/movies/score-plot route.
    """
    print("Testing /api/movies/score-plot route on the output")
    # Test with IDs of 2 popular movies (the Minecraft movie and Mufasa: The Lion King)
    movie_ids = [950387, 1021004]
    response = session.get(f"{BASE_URL}/api/movies/score-plot?movie_ids={','.join(map(str, movie_ids))}")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert len(response.content) > 0, "Expected non-empty response data"
    try:
        image = Image.open(BytesIO(response.content))
        image.verify()
    except UnidentifiedImageError as e:
        raise AssertionError(f"Image is not valid: {e}")
    except IOError as e:
        raise AssertionError(f"Image is not valid: {e}")


def get_score_plot_invalid_movie_ids():
    """
    Test the /api/movies/score-plot route with invalid movie IDs.
    """
    print("Testing /api/movies/score-plot route for input using invalid movie IDs")
    # Test with invalid movie IDs
    movie_ids = [0]
    response = session.get(f"{BASE_URL}/api/movies/score-plot?movie_ids={','.join(map(str, movie_ids))}")
    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"


def get_score_plot_no_movie_ids():
    """
    Test the /api/movies/score-plot route with no movie IDs.
    """
    print("Testing /api/movies/score-plot route for input using no input IDs")
    # Test with no movie IDs
    movie_ids = []
    response = session.get(f"{BASE_URL}/api/movies/score-plot?movie_ids={','.join(map(str, movie_ids))}")
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"


def add_and_remove_favorite_movie():
    """
    Test the /api/movies/favorite/{movie_id} route.
    """
    print("Testing /api/movies/favorite/{movie_id} route with adding and deleting movies")
    # Test with invalid movie ID
    response = session.post(f"{BASE_URL}/api/movies/favorite/{0}", headers=CSFR_headers)
    assert response.status_code == 404

    # Test by adding the minecraft movie to favorites
    response = session.get(f"{BASE_URL}/api/movies/favorite/{950387}")
    assert isinstance(response.json()["is_favorite"], bool)
    in_favorites = response.json()["is_favorite"]
    assert response.status_code == 200

    # If it is in favorites, remove it
    if in_favorites:
        response = session.delete(f"{BASE_URL}/api/movies/favorite/{950387}", headers=CSFR_headers)
        assert response.status_code == 200
        assert response.json() == {"message": "Movie removed from favorites."}

    # Test whether the movie is not in favorites
    response = session.get(f"{BASE_URL}/api/movies/favorite")
    assert response.status_code == 200
    assert "results" in response.json()
    assert isinstance(response.json()["results"], list)
    assert not any(movie["id"] == 950387 for movie in response.json()["results"])

    # Test adding the movie to favorites (the minecraft movie)
    response = session.post(f"{BASE_URL}/api/movies/favorite/{950387}", headers=CSFR_headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Movie added to favorites."}

    # Test whether the movie is in favorites
    response = session.get(f"{BASE_URL}/api/movies/favorite")
    assert response.status_code == 200
    assert "results" in response.json()
    assert isinstance(response.json()["results"], list)
    assert any(movie["id"] == 950387 for movie in response.json()["results"])

    # Test whether the movie is in favorites
    response = session.get(f"{BASE_URL}/api/movies/favorite/{950387}")
    assert response.json()["is_favorite"] is True

    # Test removing the movie from favorites
    response = session.delete(f"{BASE_URL}/api/movies/favorite/{950387}", headers=CSFR_headers)
    assert response.status_code == 200
    assert response.json() == {"message": "Movie removed from favorites."}

    # Test whether the movie is not in favorites
    response = session.get(f"{BASE_URL}/api/movies/favorite")
    assert response.status_code == 200
    assert "results" in response.json()
    assert isinstance(response.json()["results"], list)
    assert not any(movie["id"] == 950387 for movie in response.json()["results"])

    # Add it back to favorites if it was there before
    if in_favorites:
        response = session.post(f"{BASE_URL}/api/movies/favorite/{950387}", headers=CSFR_headers)
        assert response.status_code == 200
        assert response.json() == {"message": "Movie added to favorites."}


def get_movie_by_id():
    """
    Test the /movie/{movie_id} route.
    """
    print("Testing /api/movies/{movie_id} with getting a certain movie with the given ID")
    # Test with invalid movie ID
    response = session.get(f"{BASE_URL}/api/movies/{0}")
    assert response.status_code == 404

    # Test with valid movie ID (the minecraft movie)
    mc_movie_id = 950387
    response = session.get(f"{BASE_URL}/api/movies/{mc_movie_id}")
    assert response.status_code == 200
    assert "id" in response.json()
    assert "title" in response.json()
    assert "overview" in response.json()
    assert "release_date" in response.json()
    assert "poster_path" in response.json()
    assert "popularity" in response.json()
    assert "vote_average" in response.json()
    assert "vote_count" in response.json()
    assert "backdrop_path" in response.json()
    assert "adult" in response.json()
    assert "genre_ids" in response.json()
    assert isinstance(response.json()["id"], int)
    assert isinstance(response.json()["title"], str)
    assert isinstance(response.json()["overview"], str)
    assert isinstance(response.json()["release_date"], str)
    assert isinstance(response.json()["poster_path"], str)
    assert isinstance(response.json()["popularity"], float)
    assert isinstance(response.json()["vote_average"], float)
    assert isinstance(response.json()["vote_count"], int)


def get_movie_by_id_invalid():
    """
    Test the /movie/{movie_id} route with an invalid movie ID.
    """
    print("Testing /api/movie/{movie_id} route with an invalid movie ID.")
    # Test with invalid movie ID
    response = session.get(f"{BASE_URL}/api/movies/{0}")
    assert response.status_code == 404



if __name__ == "__main__":
    # Login and sign up
    session.post(f"{BASE_URL}/api/sign_up", json={"username": "user", "password": "password"})
    session.post(f"{BASE_URL}/api/login", json={"username": "user", "password": "password"})

    # Get the X-CSRF-TOKEN, you get these from logging in.
    # This is for a CSRF attack in POST and DELETE requests when using cookies.
    csrf = session.cookies.get("csrf_access_token")
    CSFR_headers = {"X-CSRF-TOKEN": csrf}

    # Run all functions in this file
    get_popular_amount()
    get_popular_content()
    get_same_genres_related_movie()
    get_same_genres_no_related_movie()
    get_same_genres_movie_itself_excluded()
    get_similar_runtime_similar()
    get_similar_runtime_not_similar()
    get_similar_runtime_movie_itself_excluded()
    get_score_plot()
    get_score_plot_invalid_movie_ids()
    get_score_plot_no_movie_ids()
    add_and_remove_favorite_movie()
    get_movie_by_id()
    get_movie_by_id_invalid()

    # Logout
    session.post(f"{BASE_URL}/api/logout")