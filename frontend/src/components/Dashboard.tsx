import React, {useEffect, useState} from 'react';
import '../css/DashBoard.css'; // Import your CSS file for custom styles
import '../css/FrontPage.css'; // Import your CSS file for custom styles
import {useNavigationHelpers} from "../routing/useNavigation";

type Movie = {
    id: number;
    title: string;
    posterUrl: string;
}

type APIMovieResponse = {
    movie_id: number;
    movie_name: string;
    poster_path: string;
}

const Dashboard: React.FC = () => {
    const [movies, setMovies] = useState<Movie[]>([]);
    const [favoriteMovieIds, setFavoriteMovieIds] = useState<Set<number>>(new Set());
    const [favoriteMovies, setFavoriteMovies] = useState<Movie[]>([])
    const {handleLogout, handleHome, goToFriends, handleMovie} = useNavigationHelpers();
    const [ratingRecommendations, setRatingRecommendations] = useState<Movie[]>([]);
    const [friendRecommendations, setFriendRecommendations] = useState<Movie[]>([]);

    // Get all the popular movies
    useEffect(() => {
        // Fetch popular movies when the component mounts
        const fetchMovies = async () => {
            try {
                const response = await fetch('/api/movies/list?amount=20');
                const data = await response.json();
                console.log('Fetched movies:', data);
                const transformed: Movie[] = data.results.map((movie: APIMovieResponse) => ({
                    id: movie.movie_id,
                    title: movie.movie_name,
                    posterUrl: movie.poster_path,
                }));
                setMovies(transformed); // Assuming the response contains an array of movies
            } catch (error) {
                console.error('Error fetching movies:', error);
            }
        };

        fetchMovies();
    }, []);

    function getCookie(name: string): string | null {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop()?.split(';')?.shift() ?? null;
        return null;
    }

    // Get the users favorite movies:
    const fetchFavoriteMovies = async () => {
        try {
            const response = await fetch('/api/preference/favorite');
            const data = await response.json();
            const transformed: Movie[] = data.results.map((movie: APIMovieResponse) => ({
                id: movie.movie_id,
                title: movie.movie_name,
                posterUrl: `https://image.tmdb.org/t/p/w500${movie.poster_path}`,
            }));
            setFavoriteMovies(transformed);
            setFavoriteMovieIds(new Set(transformed.map(m => m.id))); // Optional
        } catch (error) {
            console.error('Error fetching favorites:', error);
        }
    };

    const fetchRatingRecommendations = async () => {
        try {
            const response = await fetch('/api/preference/recommendations?amount=20');
            const data = await response.json();
            const transformed: Movie[] = data.results.map((movie: APIMovieResponse) => ({
                id: movie.movie_id,
                title: movie.movie_name,
                posterUrl: `https://image.tmdb.org/t/p/w500${movie.poster_path}`,
            }));
            setRatingRecommendations(transformed);
        } catch (error) {
            console.error('Error fetching rating recommendations:', error);
        }
    };

    const fetchFriendRecommendations = async () => {
        try {
            const response = await fetch('/api/preference/recommendations/friends?amount=20');
            const data = await response.json();
            const transformed: Movie[] = data.results.map((movie: APIMovieResponse) => ({
                id: movie.movie_id,
                title: movie.movie_name,
                posterUrl: `https://image.tmdb.org/t/p/w500${movie.poster_path}`,
            }));
            setFriendRecommendations(transformed);
        } catch (error) {
            console.error('Error fetching friend recommendations:', error);
        }
    };

    useEffect(() => {
        fetchFavoriteMovies();
        fetchRatingRecommendations();
        fetchFriendRecommendations();
    }, []);

    const toggleFavorite = async (id: number) => {
        const isFavorite = favoriteMovieIds.has(id);
        try {
            // Update local state only if API call was successful
            setFavoriteMovieIds(prev => {
                const newSet = new Set(prev);
                if (isFavorite) {
                    newSet.delete(id);
                } else {
                    newSet.add(id);
                }
                return newSet;
            });
            const csrfToken = getCookie('csrf_access_token');
            const headers: Record<string, string> = {
                'Content-Type': 'application/json',
                ...(csrfToken ? {'X-CSRF-TOKEN': csrfToken} : {}),
            };
            const response = await fetch(`/api/preference/favorite/${id}`, {
                method: isFavorite ? 'DELETE' : 'POST',
                headers: headers
            });

            await fetchFavoriteMovies(); // <-- refresh after change

            if (!response.ok) {
                throw new Error(`Failed to ${isFavorite ? 'remove' : 'add'} favorite`);
            }

            await fetchFavoriteMovies(); // <-- refresh after change
        } catch (error) {
            console.error('Error toggling favorite:', error);
        }
    };


    return (
        <div className="dashboard-container">
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
                    onClick={goToFriends}
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
                    Friends
                </button>
                <h1 className="top-bar-title">Dashboard</h1>
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

            {/* Grid of popular movies */}
            <section className="movies-section">
                <h2 className="section-title">Popular Movies</h2>
                <div className="movies-grid">
                    {movies.slice().map((movie) => (
                        <div
                            key={movie.id}
                            className="movie-card"
                        >
                            <img
                                src={movie.posterUrl}
                                alt={movie.title}
                                className="movie-poster"
                                onClick={() => handleMovie(movie.id)} // Navigate to movie page on click
                            />
                            <link rel="stylesheet"
                                  href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"/>
                            <div
                                className="star-overlay"
                                onClick={(event) => {
                                    event.stopPropagation(); // Prevent the click from propagating to the parent div
                                    toggleFavorite(movie.id);
                                }}
                            >
                                <i className={`fa-star ${favoriteMovieIds.has(movie.id) ? 'fas' : 'far'}`}></i>
                            </div>
                            <h3 className="movie-title">{movie.title}</h3>
                        </div>
                    ))}
                </div>
            </section>

            {/* Grid of favorite movies */}
            <section className="movies-section">
                <h2 className="section-title">Favorite Movies</h2>
                <div className="movies-grid">
                    {favoriteMovies.slice().map((movie) => (
                        <div key={movie.id} className="movie-card">
                            <img
                                src={movie.posterUrl}
                                alt={movie.title}
                                className="movie-poster"
                                onClick={() => handleMovie(movie.id)}
                            />
                            <div
                                className="star-overlay"
                                onClick={() => toggleFavorite(movie.id)}
                            >
                                <i className={`fa-star ${favoriteMovieIds.has(movie.id) ? 'fas' : 'far'}`}></i>
                            </div>
                            <h3 className="movie-title">{movie.title}</h3>
                        </div>
                    ))}
                </div>
            </section>

            {/* Grid of recommended by rating */}
            <section className="movies-section">
                <h2 className="section-title">Recommended by Rating</h2>
                <div className="movies-grid">
                    {ratingRecommendations.map((movie) => (
                        <div key={movie.id} className="movie-card">
                            <img
                                src={movie.posterUrl}
                                alt={movie.title}
                                className="movie-poster"
                                onClick={() => handleMovie(movie.id)}
                            />
                            <div
                                className="star-overlay"
                                onClick={() => toggleFavorite(movie.id)}
                            >
                                <i className={`fa-star ${favoriteMovieIds.has(movie.id) ? 'fas' : 'far'}`}></i>
                            </div>
                            <h3 className="movie-title">{movie.title}</h3>
                        </div>
                    ))}
                </div>
            </section>

            {/* Grid of recommended by friends watched */}
            <section className="movies-section">
                <h2 className="section-title">Recommended by Friends</h2>
                <div className="movies-grid">
                    {friendRecommendations.map((movie) => (
                        <div key={movie.id} className="movie-card">
                            <img
                                src={movie.posterUrl}
                                alt={movie.title}
                                className="movie-poster"
                                onClick={() => handleMovie(movie.id)}
                            />
                            <div
                                className="star-overlay"
                                onClick={() => toggleFavorite(movie.id)}
                            >
                                <i className={`fa-star ${favoriteMovieIds.has(movie.id) ? 'fas' : 'far'}`}></i>
                            </div>
                            <h3 className="movie-title">{movie.title}</h3>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
};

export default Dashboard;
