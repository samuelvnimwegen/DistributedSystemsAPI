"""
Test the movie resource, and all the routes in it.
"""


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
