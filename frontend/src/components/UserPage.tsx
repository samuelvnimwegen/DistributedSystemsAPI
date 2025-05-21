import { useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useNavigationHelpers } from "../routing/useNavigation.tsx";
import { fetchMoviesByIds } from "../movies/fetchMoviesByIds.tsx";
import '../css/UserPage.css';

type Movie = {
    movie_id: number;
    movie_name: string;
    poster_path: string;
};

type Rating = {
    movie_id: number;
    rating: number;
};


const UserPage = () => {
    const { user_id } = useParams();
    const [watchedMovies, setWatchedMovies] = useState<Movie[]>([]);
    const [ratings, setRatings] = useState<(Rating & Movie)[]>([]);
    const [loading, setLoading] = useState(true);
    const { handleLogout, handleHome, goToDashboard } = useNavigationHelpers();

    useEffect(() => {
        const fetchUserData = async () => {
            try {
                const watchedRes = await fetch(`/api/activity/watched?user_id=${user_id}`);
                const ratingsRes = await fetch(`/api/preference/rating/friends/${user_id}`);

                if (!watchedRes.ok || !ratingsRes.ok) throw new Error();

                const watchedData = await watchedRes.json();
                const ratingsData = await ratingsRes.json();

                const watchedIds = watchedData.results.map((entry: Rating) => entry.movie_id);
                const ratingEntries = ratingsData.results;

                const ratingIds = ratingEntries.map((entry: Rating) => entry.movie_id);

                const [watchedMoviesData, ratedMoviesData] = await Promise.all([
                    fetchMoviesByIds(watchedIds),
                    fetchMoviesByIds(ratingIds)
                ]);

                setWatchedMovies(watchedMoviesData);

                const ratingsWithMovieDetails = ratingEntries.map((entry: Rating) => {
                    const matched = ratedMoviesData.find((m: { id: number; }) => m.id === entry.movie_id);
                    return matched
                        ? {
                            movie_id: entry.movie_id,
                            rating: entry.rating,
                            title: matched.title,
                            posterUrl: matched.posterUrl,
                            id: matched.id,
                        }
                        : null;
                }).filter(Boolean) as (Rating & Movie)[];

                setRatings(ratingsWithMovieDetails);
            } catch (err) {
                console.error("Failed to load user data:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchUserData();
    }, [user_id]);

    if (loading) return <div>Loading user data...</div>;

    return (
        <div className="user-page">
            <header className="top-bar">
                <button
                    onClick={handleLogout}
                    className="login-button"
                    style={{
                        position: 'absolute',
                        right: '20px',
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
                        right: '125px',
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
                <h1 className="top-bar-title">User Profile</h1>
                <button
                    onClick={handleHome}
                    className="login-button"
                    style={{
                        position: 'absolute',
                        left: '20px',
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

            <section className="movies-section">
                <h2>Recently Watched</h2>
                <div className="movies-grid">
                    {watchedMovies.map((movie) => (
                        <div key={movie.movie_id} className="movie-card">
                            <img src={movie.poster_path} alt={movie.movie_name} className="movie-poster" />
                            <h3 className="movie-title">{movie.movie_name}</h3>
                        </div>
                    ))}
                    {watchedMovies.length === 0 && <p>No movies watched yet.</p>}
                </div>
            </section>

            <section className="movies-section">
                <h2>Movie Ratings</h2>
                <div className="ratings-list">
                    {ratings.map((r) => (
                        <div key={r.movie_id} className="rating-item">
                            <img src={r.poster_path} alt={r.movie_name} className="movie-poster small" />
                            <div>
                                <strong>{r.movie_name}</strong> — {r.rating}/10
                            </div>
                        </div>
                    ))}
                    {ratings.length === 0 && <p>No ratings submitted yet.</p>}
                </div>
            </section>
        </div>
    );
};

export default UserPage;
