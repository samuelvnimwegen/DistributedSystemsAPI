import React, {useEffect, useState} from 'react';
import '../css/MovieModal.css';

type Movie = {
    id: number;
    title: string;
    posterUrl: string;
    releaseDate: string;
};

type Props = {
    movie: Movie;
    onClose: () => void;
};

type MovieDetails = {
    id: number;
    title: string;
    overview: string;
    original_language: string;
    original_title: string;
    release_date: string;
    poster_path: string;
    popularity: number;
    vote_average: number;
    vote_count: number;
    backdrop_path: string;
    adult: boolean;
    genre_ids: number[];
};

const MovieModal: React.FC<Props> = ({movie, onClose}) => {
    const [movieDetails, setMovieDetails] = useState<MovieDetails | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [similarMovies, setSimilarMovies] = useState<Movie[]>([]);
    const [similarRunTimeMovies, setSimilarRunTimeMovies] = useState<Movie[]>([]);
    const [selectedMovieIds, setSelectedMovieIds] = useState<Set<number>>(new Set());
    const [imageDataUrl, setImageDataUrl] = useState<string>("");
    const [scorePlotActive, setScorePlotActive] = useState(false);


    useEffect(() => {
        const fetchSimilarMovies = async () => {
            try {
                const response = await fetch(`/api/movies/${movie.id}/same_genres`);
                const data = await response.json();
                // Transform the response to match the Movie type
                const transformedMovies = data.results.map((movie: MovieDetails) => ({
                    id: movie.id,
                    title: movie.title,
                    posterUrl: movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : 'https://via.placeholder.com/150',
                    releaseDate: movie.release_date,
                }));
                setSimilarMovies(transformedMovies);
            } catch (error) {
                console.error('Error fetching similar movies:', error);
            }
        };

        fetchSimilarMovies();
    }, [movieDetails]);

    useEffect(() => {
        const fetchSimilarRuntime = async () => {
            try {
                const response = await fetch(`/api/movies/${movie.id}/similar_runtime`);
                const data = await response.json();
                // Transform the response to match the Movie type
                const transformedMovies = data.results.map((movie: MovieDetails) => ({
                    id: movie.id,
                    title: movie.title,
                    posterUrl: movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : 'https://via.placeholder.com/150',
                    releaseDate: movie.release_date,
                }));
                setSimilarRunTimeMovies(transformedMovies);
            } catch (error) {
                console.error('Error fetching similar movies:', error);
            }
        };

        fetchSimilarRuntime();
    }, [movieDetails]);

    // Function to fetch movie details
    const fetchMovieDetails = async (id: number) => {
        try {
            const response = await fetch(`/api/movies/${id}`);
            if (!response.ok) {
                throw new Error('Failed to fetch movie details');
            }
            const data: MovieDetails = await response.json();
            setMovieDetails(data);
        } catch (error) {
            if (error instanceof Error) {
                setError(error.message);
            }
        } finally {
            setLoading(false);
        }
    };

    // Fetch movie details when component mounts
    useEffect(() => {
        if (movie.id) {
            fetchMovieDetails(movie.id);
        }
    }, [movie.id]);

    // Render the movie details
    if (loading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    const toggleSelectMovie = (id: number) => {
        setSelectedMovieIds(prev => {
            const newSet = new Set(prev);
            if (newSet.has(id)) {
                newSet.delete(id);
            } else {
                newSet.add(id);
            }
            return newSet;
        });
    };

    const fetchScorePlot = async () => {
        const movieIdsArray = Array.from(selectedMovieIds);
        if (movieIdsArray.length === 0) {
            console.warn("No movies selected");
            return;
        }
        const total_array = movie.id + ',' + movieIdsArray.join(',');
        const apiUrl = `/api/movies/score-plot?movie_ids=${total_array}`;

        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`Failed to fetch: ${response.statusText}`);
            }
            const blob = await response.blob(); // Get the response as a Blob
            const reader = new FileReader();
            reader.onloadend = () => {
                setImageDataUrl(reader.result as string); // Convert Blob to data URL
            };
            reader.readAsDataURL(blob);
            setScorePlotActive(true);
            // You can now store this in state or use it however you like
        } catch (error) {
            console.error('Error fetching score plot:', error);
        }
    };

    return (
        <div className="modal-backdrop" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="close-button" onClick={onClose}>X</button>
                <div className="modal-body">
                    <div className="main-movie">
                        <img
                            src={movie.posterUrl}
                            alt={movie.title}
                            className="modal-poster"
                        />
                        <div className="movie-details">
                            <h2 className="movie-title" style={{color: "darkblue"}}>{movie.title}</h2>
                            <p className="release-date">Release Date: <span>{movie.releaseDate}</span></p>
                            <p className="overview"><strong>Overview:</strong> {movieDetails?.overview}</p>
                            <p><strong>Original Language:</strong> {movieDetails?.original_language}</p>
                            <p><strong>Original Title:</strong> {movieDetails?.original_title}</p>
                            <p><strong>Popularity:</strong> {movieDetails?.popularity}</p>
                            <p><strong>Vote Average:</strong> {movieDetails?.vote_average}</p>
                            <p><strong>Vote Count:</strong> {movieDetails?.vote_count}</p>
                            <p><strong>Adult Content:</strong> {movieDetails?.adult ? 'Yes' : 'No'}</p>
                        </div>
                    </div>

                    <div className="similar-movies">
                        <h3 style={{color: "black", alignSelf: "flex-start"}}>Similar Movies</h3>
                        <div className="movies-list">
                            {similarMovies.slice(0, 5).map((movie) => (
                                <div key={movie.id}
                                     className={`movie-card ${selectedMovieIds.has(movie.id) ? 'selected' : ''}`}
                                     onClick={() => toggleSelectMovie(movie.id)}>
                                    <img src={movie.posterUrl} alt={movie.title} className="movie-poster"/>
                                    <h4>{movie.title}</h4>
                                </div>
                            ))}
                        </div>
                        <h3 style={{color: "black", alignSelf: "flex-start"}}>Movies with Similar Runtime</h3>
                        <div className="movies-list">
                            {similarRunTimeMovies.slice(0, 5).map((movie) => (
                                <div key={movie.id}
                                     className={`movie-card ${selectedMovieIds.has(movie.id) ? 'selected' : ''}`}
                                     onClick={() => toggleSelectMovie(movie.id)}>
                                    <img src={movie.posterUrl} alt={movie.title} className="movie-poster"/>
                                    <h4>{movie.title}</h4>
                                </div>
                            ))}
                        </div>
                        <button onClick={fetchScorePlot} style={{marginTop: "20px"}}>Get Score Plot</button>
                        {scorePlotActive && <img src={imageDataUrl} alt="Fetched Raw Image" />}
                    </div>
                </div>
            </div>

        </div>
    );
};

export default MovieModal;
