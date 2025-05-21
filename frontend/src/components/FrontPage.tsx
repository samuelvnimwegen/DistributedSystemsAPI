import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom'; // Import useHistory to handle navigation
import '../css/FrontPage.css';
import {useAuth} from "../auth/AuthContext.tsx"; // Import your CSS file for custom styles

type Movie = {
  id: number;
  title: string;
  posterUrl: string;
  releaseDate: string;
};

type APIMovieResponse = {
  id: number;
  title: string;
  poster_path: string;
  release_date: string;
}

const FrontPage: React.FC = () => {
  const [movies, setMovies] = useState<Movie[]>([]);
  const navigate = useNavigate(); // Get the navigate function
    const { isAuthenticated } = useAuth();

  useEffect(() => {
    const fetchMovies = async () => {
      try {
        const response = await fetch('/api/movies/list?amount=20');
        const data = await response.json();

        const transformed: Movie[] = data.results.map((movie: APIMovieResponse) => ({
          id: movie.id,
          title: movie.title,
          posterUrl: `https://image.tmdb.org/t/p/w500${movie.poster_path}`,
          releaseDate: movie.release_date,
        }));

        setMovies(transformed);
      } catch (error) {
        console.error('Failed to fetch movies:', error);
      }
    };

    fetchMovies();
  }, []);

  if (movies.length === 0) {
    return (
      <div className="p-6 max-w-7xl mx-auto text-center text-lg text-gray-500">
        Loading movies...
      </div>
    );
  }
    const handleLoginClick = () => {
    navigate('/login'); // Redirect to /login when the login button is clicked
  };


  return (
    <div style={{paddingTop: '0'}}>
      <header className="top-bar">
          {!isAuthenticated && <button
              onClick={handleLoginClick}
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
              Login
          </button>}
        <h1 className="top-bar-title">Welcome to NextFilm</h1>
          {isAuthenticated && <button
              onClick={() => navigate('/dashboard')}
              className="login-button"
              style={{
                  position: 'absolute',
                  right: '20px', // Changed from left to right
                  top: '20px',
                  padding: '10px 20px',
                  backgroundColor: 'white',
                  color: 'black',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer'
              }}
          >
              Dashboard
          </button>}
      </header>

      {/* Featured Movie Section */}
      <section className="featured-section featured-container">
        <h2 className="text-2xl font-semibold mb-4">Featured Movie</h2>
        <div className="bg-gray-800 text-white rounded-lg overflow-hidden shadow-lg flex flex-col md:flex-row transition-transform duration-300 hover:scale-105 hover:shadow-2xl cursor-pointer">
          <img
            src={movies[0]?.posterUrl}
            alt={movies[0]?.title}
            className="w-full md:w-1/3 object-cover"
          />
          <div className="p-6">
            <h3 className="text-3xl font-bold">{movies[0]?.title}</h3>
          </div>
        </div>
      </section>

      {/* Popular Picks Section with Rotating Bar */}
      <section className="full-width-section">
        <h2 className="text-2xl font-semibold mb-4">Popular Movies</h2>
        <div className="scroll-container">
          {/* Rotating container */}
          <div className="scrolling-row">
            {movies.map((movie) => (
              <div key={movie.id} className="movie-card">
                <img
                  src={movie.posterUrl}
                  alt={movie.title}
                  className="movie-image"
                />
                <div className="movie-details">
                  <h3 className="movie-title">{movie.title}</h3>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};


export default FrontPage;
