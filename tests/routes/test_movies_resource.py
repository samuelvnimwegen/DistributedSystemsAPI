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
    response = client.get("/api/movies/popular?amount=21")
    assert response.status_code == 400
    assert response.json == {"message": "Maximum amount allowed amount is 20."}

    response = client.get("/api/movies/popular?amount=0")
    assert response.status_code == 400
    assert response.json == {"message": "Minimum amount allowed amount is 1."}

    # Test with valid amounts
    response = client.get("/api/movies/popular?amount=1")
    assert response.status_code == 200
    assert "results" in response.json
    assert isinstance(response.json["results"], list)
    assert len(response.json["results"]) == 1

    response = client.get("/api/movies/popular?amount=5")
    assert response.status_code == 200
    assert "results" in response.json
    assert isinstance(response.json["results"], list)
    assert len(response.json["results"]) == 5

    response = client.get("/api/movies/popular?amount=20")
    assert response.status_code == 200
    assert "results" in response.json
    assert isinstance(response.json["results"], list)
    assert len(response.json["results"]) == 20

    # No amount specified
    response = client.get("/api/movies/popular")
    assert response.status_code == 200
    assert "results" in response.json
    assert isinstance(response.json["results"], list)
    assert len(response.json["results"]) == 1


def test_get_popular_content(client):
    """
    Test the /popular route for valid content.
    """
    response = client.get("/api/movies/popular?amount=1")
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
    assert any(movie["title"] == "Snow White" for movie in response.json["results"])


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
