import React, {useEffect, useState} from 'react';
import {useParams} from 'react-router-dom';
import '../css/MoviePage.css';
import {useNavigationHelpers} from '../routing/useNavigation';

type Genre = {
    genre_id: number;
    genre_name: string;
};

type Movie = {
    movie_id: number;
    movie_name: string;
    plot: string;
    poster_path: string;
    rating: number;
    genres: Genre[];
    meta_score: number;
    runtime: number;
};


type RatingWithUsername = {
    user_id: number;
    username: string;
    rating: number;
    rating_id: number;
};


export const MoviePage: React.FC = () => {
    const {movie_id} = useParams<{ movie_id: string }>();
    const [movie, setMovie] = useState<Movie | null>(null);
    const [userRating, setUserRating] = useState<number>(0);
    const [allRatings, setAllRatings] = useState<RatingWithUsername[]>([]);
    const [watched, setWatched] = useState(false);
    const {handleLogout, handleHome, goToDashboard} = useNavigationHelpers();

    useEffect(() => {
        const fetchMovie = async () => {
            try {
                const response = await fetch(`/api/movies/${movie_id}`);
                const data = await response.json();
                setMovie(data);
            } catch (error) {
                console.error('Error fetching movie:', error);
            }
        };

        const fetchRatings = async () => {
            try {
                const response = await fetch(`/api/preference/rating/${movie_id}`);
                const data = await response.json();
                setAllRatings(data.results); // Assuming array of { user, score }
            } catch (error) {
                console.error('Error fetching ratings:', error);
            }
        };

        fetchMovie();
        fetchRatings();
    }, [movie_id]);

    useEffect(() => {
        const checkWatched = async () => {
            try {
                const response = await fetch(`/api/activity/watched/${movie_id}`);
                const data = await response.json();
                setWatched(data.message === "Movie is watched.");
            } catch (err) {
                console.error("Failed to check watched status", err);
            }
        };

        checkWatched();
    }, [movie_id])

    useEffect(() => {
        const fetchRatingsWithUsernames = async () => {
            try {
                const response = await fetch(`/api/preference/rating/${movie_id}`, {
                    method: 'GET',
                    headers: {'Content-Type': 'application/json'}
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch ratings');
                }

                const data = await response.json();
                const ratings: RatingWithUsername[] = data.results;  // ✅ Accessing results here

                const uniqueUserIds = [...new Set(ratings.map(r => r.user_id))];
                const idToUsername: Record<number, string> = {};

                await Promise.all(
                    uniqueUserIds.map(async (user_id) => {
                        try {
                            const res = await fetch(`/api/users/retrieve/${user_id}`);
                            if (!res.ok) {
                                throw new Error();
                            }
                            const userData: { username: string; user_id: number } = await res.json();
                            idToUsername[user_id] = userData.username;
                        } catch (err) {
                            console.error(`Failed to retrieve username for user ${user_id}, error:`, err);
                            idToUsername[user_id] = 'Unknown';
                        }
                    })
                );

                const combined: RatingWithUsername[] = ratings.map((r) => ({
                    user_id: r.user_id,
                    rating: r.rating,
                    username: idToUsername[r.user_id] || 'Unknown',
                    rating_id: r.rating_id
                }));

                setAllRatings(combined);
            } catch (err) {
                console.error('Error fetching ratings and usernames:', err);
            }
        };

        fetchRatingsWithUsernames();
    }, [movie_id]);

    const submitRating = async () => {
        try {
            const response = await fetch(`/api/preference/rating/${movie_id}?rating=${userRating}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json', "X-CSRF-TOKEN": getCookie('csrf_access_token')},
            });

            if (response.ok) {
                await response.json();
                setUserRating(0);
                const refreshed = await fetch(`/api/preference/rating/${movie_id}`, {
                    method: 'GET',
                    headers: {'Content-Type': 'application/json'}
                });
                const data = await refreshed.json();
                setAllRatings(data.results);
            }
        } catch (error) {
            console.error('Error submitting rating:', error);
        }
    };

    const handleWatch = async () => {
        try {
            const response = await fetch(`/api/activity/watched/${movie_id}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': getCookie('csrf_access_token')
                }
            });

            if (response.ok) {
                setWatched(true);
            } else {
                console.error("Failed to mark as watched");
            }
        } catch (error) {
            console.error("Error watching movie:", error);
        }
    };

    const handleReviewReaction = async (ratingId: number, reaction: 'like' | 'dislike') => {
    try {
        const agreed: boolean = reaction === 'like';
        const response = await fetch(`/api/rating_review/${ratingId}?agreed=${agreed}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': getCookie('csrf_access_token'),
            },
        });

        if (!response.ok) {
            throw new Error('Reaction failed');
        }

    } catch (error) {
        console.error(`Error reacting to review:`, error);
    }
};

    function getCookie(name: string): string {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop()?.split(';')?.shift() ?? "";
        return "";
    }

    if (!movie) return <div>Loading...</div>;

    return (
        <div className="movie-detail-container">
            <header className="top-bar">
                <button
                    onClick={handleLogout}
                    className="login-button"
                    style={{
                        position: 'absolute',
                        right: '20px', // Changed from left to right
                        top: '20px',
                        padding: '10px 20px',
                        backgroundColor: '#4CAF50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer'
                    }}
                >
                    Log Out
                </button>
                <button
                    onClick={goToDashboard}
                    className="login-button"
                    style={{
                        position: 'absolute',
                        right: '125px', // Changed from left to right
                        top: '20px',
                        padding: '10px 20px',
                        backgroundColor: '#4CAF50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer'
                    }}
                >
                    Dashboard
                </button>
                <h1 className="top-bar-title">Movie View</h1>
                <button
                    onClick={handleHome}
                    className="login-button"
                    style={{
                        position: 'absolute',
                        left: '20px', // Changed from left to right
                        top: '20px',
                        padding: '10px 20px',
                        backgroundColor: 'white',
                        color: 'black',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer'
                    }}
                >
                    Home
                </button>
            </header>
            <h1 className="movie-title">{movie.movie_name}</h1>
            <div className="movie-content">
                <img
                    className="movie-poster"
                    src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                    alt={movie.movie_name}
                />
                <div className="movie-info">
                    <p><strong>Plot:</strong> {movie.plot}</p>
                    <p><strong>Runtime:</strong> {movie.runtime} min</p>
                    <p><strong>Genres:</strong> {movie.genres.map(g => g.genre_name).join(', ')}</p>
                    <p><strong>Rating:</strong> {movie.rating}/10</p>
                    <p><strong>Metascore:</strong> {movie.meta_score}</p>
                    <button
                        className="watch-button"
                        onClick={handleWatch}
                        disabled={watched}
                    >
                        {watched ? "✅ Watched" : "🎬 Watch"}
                    </button>
                </div>
            </div>

            <div className="rating-section">
                <h3>Rate this movie:</h3>
                <input
                    type="number"
                    min="1"
                    max="10"
                    value={userRating}
                    onChange={(e) => setUserRating(Number(e.target.value))}
                />
                <button onClick={submitRating}>Submit Rating</button>
            </div>

            <div className="existing-ratings">
                <h3>User Ratings</h3>
                <ul>
                    {allRatings.map((r, i) => (
                        <li key={i}>
                            {r.username}: {r.rating}/10
                            <button
                                className="like-button"
                                onClick={() => handleReviewReaction(r.rating_id, 'like')}
                            >
                                👍
                            </button>
                            <button
                                className="dislike-button"
                                onClick={() => handleReviewReaction(r.rating_id, 'dislike')}
                            >
                                👎
                            </button>
                        </li>
                    ))}
                </ul>
            </div>
        </div>

    );
};

export default MoviePage;
