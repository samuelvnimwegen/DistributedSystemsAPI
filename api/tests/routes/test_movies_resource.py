"""
Test the movie resource, and all the routes in it.
"""
from io import BytesIO
from PIL import Image, UnidentifiedImageError
import pytest


def assert_correct_film_list(response) -> None:
    """
    Assert that the response is a correct film list.
    :param response: The response to check
    :return: None
    """
    assert response.status_code == 200
    assert "results" in response.json
    assert isinstance(response.json["results"], list)
    assert len(response.json["results"]) > 0


def test_get_popular_amount(client):
    """
    Test the /popular route with different amounts.
    """
    # Test with invalid amounts
    response = client.get("/api/movies?amount=21")
    assert response.status_code == 400
    assert response.json == {"message": "Maximum amount allowed amount is 20."}

    response = client.get("/api/movies?amount=0")
    assert response.status_code == 400
    assert response.json == {"message": "Minimum amount allowed amount is 1."}

    # Test with valid amounts
    response = client.get("/api/movies?amount=1")
    assert response.status_code == 200
    assert "results" in response.json
    assert isinstance(response.json["results"], list)
    assert len(response.json["results"]) == 1

    response = client.get("/api/movies?amount=5")
    assert response.status_code == 200
    assert "results" in response.json
    assert isinstance(response.json["results"], list)
    assert len(response.json["results"]) == 5

    response = client.get("/api/movies?amount=20")
    assert response.status_code == 200
    assert "results" in response.json
    assert isinstance(response.json["results"], list)
    assert len(response.json["results"]) == 20

    # No amount specified
    response = client.get("/api/movies")
    assert response.status_code == 200
    assert "results" in response.json
    assert isinstance(response.json["results"], list)
    assert len(response.json["results"]) == 1


def test_get_popular_content(client):
    """
    Test the /popular route for valid content.
    """
    response = client.get("/api/movies?amount=1")
    assert response.status_code == 200
    assert "results" in response.json
    assert isinstance(response.json["results"], list)
    assert len(response.json["results"]) == 1

    movie = response.json["results"][0]
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


def test_get_same_genres_related_movie(client):
    """
    Test the /same_genres route with a related movie.
    """
    # Test with invalid movie_id
    response = client.get(f"/api/movies/{0}/same_genres")
    assert response.status_code == 404

    # Test with ID of a popular movie (the Minecraft movie)
    mc_movie_id = 950387
    response = client.get(f"/api/movies/{mc_movie_id}/same_genres")
    assert response.status_code == 200

    # See that the movie with the title "Shrek" is in the list of related movies
    assert_correct_film_list(response)
    assert any(movie["title"] == "Shrek" for movie in response.json["results"])


def test_get_same_genres_no_related_movie(client):
    """
    Test the /same_genres route with a movie that has no related movies.
    """
    # Test with ID of a movie that Shrek is not related to (Captain America: Brave New World)
    cap_america_id = 822119
    response = client.get(f"/api/movies/{cap_america_id}/same_genres")
    assert response.status_code == 200

    # See that the movie with the title "Shrek" is not in the list of related movies
    assert_correct_film_list(response)
    assert not any(movie["title"] == "Shrek" for movie in response.json["results"])


def test_get_same_genres_movie_itself_excluded(client):
    """
    Test the /same_genres route to see whether the movie that is queried is not in the results.
    """
    # Test with ID of a popular movie (the Minecraft movie)
    mc_movie_id = 950387
    response = client.get(f"/api/movies/{mc_movie_id}/same_genres")
    assert response.status_code == 200

    # See that the movie with the title "Shrek" is not in the list of related movies
    assert_correct_film_list(response)
    assert not any(movie["title"] == "A Minecraft Movie" for movie in response.json["results"])


def test_get_similar_runtime_similar(client):
    """
    Test the /similar_runtime route with a movie that has similar runtime.
    """
    # Test with ID of a popular movie (the Minecraft movie)
    mc_movie_id = 950387
    response = client.get(f"/api/movies/{mc_movie_id}/similar_runtime")
    assert_correct_film_list(response)


def test_get_similar_runtime_not_similar(client):
    """
    Test the /similar_runtime route with a movie that has not similar runtime.
    """
    # Test with ID of a popular movie (the Minecraft movie)
    mc_movie_id = 950387
    response = client.get(f"/api/movies/{mc_movie_id}/similar_runtime")
    assert_correct_film_list(response)
    assert not any(movie["title"] == "Interstellar" for movie in response.json["results"])


def test_get_similar_runtime_movie_itself_excluded(client):
    """
    Test the /similar_runtime route to see whether the movie that is queried is not in the results.
    """
    # Test with ID of a popular movie (the Minecraft movie)
    mc_movie_id = 950387
    response = client.get(f"/api/movies/{mc_movie_id}/similar_runtime")
    assert_correct_film_list(response)
    assert not any(movie["title"] == "A Minecraft Movie" for movie in response.json["results"])


def test_get_score_plot(client):
    """
    Test the /score-plot route.
    """
    # Test with IDs of 2 popular movies (the Minecraft movie and Mufasa: The Lion King)
    movie_ids = [950387, 1021004]
    response = client.get("/api/movies/score-plot", query_string={"movie_ids": ",".join(map(str, movie_ids))})
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    assert response.content_type.startswith("image/"), f"Expected content type image/, got {response.content_type}"
    assert len(response.data) > 0, "Expected non-empty response data"
    try:
        image = Image.open(BytesIO(response.data))
        image.verify()
    except UnidentifiedImageError as e:
        pytest.fail(f"Invalid image format: {e}")
    except IOError as e:
        pytest.fail(f"IO error when opening image: {e}")


def test_get_score_plot_invalid_movie_ids(client):
    """
    Test the /score-plot route with invalid movie IDs.
    """
    # Test with invalid movie IDs
    movie_ids = [0]
    response = client.get("/api/movies/score-plot", query_string={"movie_ids": ",".join(map(str, movie_ids))})
    assert response.status_code == 404, f"Expected status code 404, got {response.status_code}"


def test_get_score_plot_no_movie_ids(client):
    """
    Test the /score-plot route with no movie IDs.
    """
    # Test with no movie IDs
    movie_ids = []
    response = client.get("/api/movies/score-plot", query_string={"movie_ids": ",".join(map(str, movie_ids))})
    assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"


def test_add_and_remove_favorite_movie(client):
    """
    Test the /add-favorite route.
    """
    # Test with invalid movie ID
    # Make an auth header:
    headers = {"X-CSRF-TOKEN": client.csrf_token}
    response = client.post(f"/api/movies/favorite/{0}", headers=headers)
    assert response.status_code == 404

    # Test by adding the minecraft movie to favorites
    response = client.get(f"/api/movies/favorite/{950387}")
    assert isinstance(response.json["is_favorite"], bool)
    in_favorites = response.json["is_favorite"]
    assert response.status_code == 200

    # If it is in favorites, remove it
    if in_favorites:
        response = client.delete(f"/api/movies/favorite/{950387}", headers=headers)
        assert response.status_code == 200
        assert response.json == {"message": "Movie removed from favorites."}

    # Test whether the movie is not in favorites
    response = client.get("/api/movies/favorite")
    assert response.status_code == 200
    assert "results" in response.json
    assert isinstance(response.json["results"], list)
    assert not any(movie["id"] == 950387 for movie in response.json["results"])

    # Test adding the movie to favorites (the minecraft movie)
    response = client.post(f"/api/movies/favorite/{950387}", headers=headers)
    assert response.status_code == 200
    assert response.json == {"message": "Movie added to favorites."}

    # Test whether the movie is in favorites
    response = client.get("/api/movies/favorite")
    assert response.status_code == 200
    assert "results" in response.json
    assert isinstance(response.json["results"], list)
    assert any(movie["id"] == 950387 for movie in response.json["results"])

    # Test whether the movie is in favorites
    response = client.get(f"/api/movies/favorite/{950387}")
    assert response.json["is_favorite"] is True

    # Test removing the movie from favorites
    response = client.delete(f"/api/movies/favorite/{950387}", headers=headers)
    assert response.status_code == 200
    assert response.json == {"message": "Movie removed from favorites."}

    # Test whether the movie is not in favorites
    response = client.get("/api/movies/favorite")
    assert response.status_code == 200
    assert "results" in response.json
    assert isinstance(response.json["results"], list)
    assert not any(movie["id"] == 950387 for movie in response.json["results"])

    # Add it back to favorites if it was there before
    if in_favorites:
        response = client.post(f"/api/movies/favorite/{950387}", headers=headers)
        assert response.status_code == 200
        assert response.json == {"message": "Movie added to favorites."}


def test_get_movie_by_id(client):
    """
    Test the /movie/{movie_id} route.
    """
    # Test with invalid movie ID
    response = client.get(f"/api/movies/{0}")
    assert response.status_code == 404

    # Test with valid movie ID (the minecraft movie)
    mc_movie_id = 950387
    response = client.get(f"/api/movies/{mc_movie_id}")
    assert response.status_code == 200
    assert "id" in response.json
    assert "title" in response.json
    assert "overview" in response.json
    assert "release_date" in response.json
    assert "poster_path" in response.json
    assert "popularity" in response.json
    assert "vote_average" in response.json
    assert "vote_count" in response.json
    assert "backdrop_path" in response.json
    assert "adult" in response.json
    assert "genre_ids" in response.json
    assert isinstance(response.json["id"], int)
    assert isinstance(response.json["title"], str)
    assert isinstance(response.json["overview"], str)
    assert isinstance(response.json["release_date"], str)
    assert isinstance(response.json["poster_path"], str)
    assert isinstance(response.json["popularity"], float)
    assert isinstance(response.json["vote_average"], float)
    assert isinstance(response.json["vote_count"], int)


def test_get_movie_by_id_invalid(client):
    """
    Test the /movie/{movie_id} route with an invalid movie ID.
    """
    # Test with invalid movie ID
    response = client.get(f"/api/movies/{0}")
    assert response.status_code == 404
