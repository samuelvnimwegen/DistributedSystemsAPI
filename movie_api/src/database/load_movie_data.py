import logging

import pandas as pd
from flask import Flask
from sqlalchemy.orm import Session
from src.database import Movie, Genre


def load_data_in_background(db_session: Session, flask_app: "Flask") -> None:
    """
    Load movie data in the background.
    """
    # This function will run the loading task in the background
    with flask_app.app_context():
        load_movie_data(db_session=db_session)


def load_movie_data(db_session: Session) -> None:
    """
    Load movie data from CSV file into the database.
    """
    # Check whether the database is empty
    if db_session.query(Movie).count() > 0:
        logging.info("Database already populated. Skipping data load.")
        return

    data = pd.read_csv('src/database/movie_data/Top_10000_Movies_IMDb.csv')
    data = data[['ID', 'Movie Name', 'Rating', 'Runtime', 'Genre', 'Metascore', 'Plot']]

    for _, row in data.iterrows():
        try:
            # Parse and validate fields
            movie_name = str(row['Movie Name']).strip()
            rating = float(row['Rating']) if not pd.isna(row['Rating']) else 0.0
            runtime = int(row['Runtime'].replace(" min", "")) if not pd.isna(row['Runtime']) else 90
            meta_score_value = row.get("Metascore")
            meta_score = int(meta_score_value) if pd.notna(meta_score_value) else None
            plot = str(row['Plot']).strip() if not pd.isna(row['Plot']) else "No plot available"

            # Create Movie instance
            movie = Movie(
                movie_name=movie_name,
                rating=rating,
                runtime=runtime,
                meta_score=meta_score,
                plot=plot
            )
            db_session.add(movie)

            # Handle genres (comma-separated)
            genres_raw = row['Genre']
            genre_names = [g.strip() for g in genres_raw.split(',')] if pd.notna(genres_raw) else []

            for genre_name in genre_names:
                # Check if genre already exists
                genre = db_session.query(Genre).filter(Genre.genre_name == genre_name).first()
                if not genre:
                    genre = Genre(genre_name=genre_name)
                    db_session.add(genre)
                movie.genres.append(genre)

            db_session.add(movie)
            db_session.commit()

        except Exception as e:  # pylint: disable=broad-exception-caught
            logging.error("Error loading movie data: %s", e)
    logging.info("Database populated.")
    db_session.commit()
