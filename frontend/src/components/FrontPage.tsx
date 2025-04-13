import React from 'react';

type Movie = {
  id: number;
  title: string;
  posterUrl: string;
  releaseDate: string;
};

const sampleMovies: Movie[] = [
  {
    id: 1,
    title: 'Inception',
    posterUrl: 'https://image.tmdb.org/t/p/w500/qmDpIHrmpJINaRKAfWQfftjCdyi.jpg',
    releaseDate: '2010-07-16',
  },
  {
    id: 2,
    title: 'The Dark Knight',
    posterUrl: 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
    releaseDate: '2008-07-18',
  },
  {
    id: 3,
    title: 'Interstellar',
    posterUrl: 'https://image.tmdb.org/t/p/w500/rAiYTfKGqDCRIIqo664sY9XZIvQ.jpg',
    releaseDate: '2014-11-07',
  },
];

const FrontPage: React.FC = () => {
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-4xl font-bold text-center mb-8">🎬 Welcome to MovieVerse</h1>

      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Featured Movie</h2>
        <div className="bg-gray-800 text-white rounded-lg overflow-hidden shadow-lg flex flex-col md:flex-row">
          <img
            src={sampleMovies[0].posterUrl}
            alt={sampleMovies[0].title}
            className="w-full md:w-1/3 object-cover"
          />
          <div className="p-6">
            <h3 className="text-3xl font-bold">{sampleMovies[0].title}</h3>
            <p className="mt-2 text-gray-300">Released: {sampleMovies[0].releaseDate}</p>
            <p className="mt-4 text-gray-400">
              Dive into a mind-bending thriller by Christopher Nolan. Explore dreams within dreams and challenge your reality.
            </p>
          </div>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-4">Popular Picks</h2>
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-6">
          {sampleMovies.map((movie) => (
            <div key={movie.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:scale-105 transition">
              <img src={movie.posterUrl} alt={movie.title} className="w-full h-72 object-cover" />
              <div className="p-4">
                <h3 className="text-xl font-semibold">{movie.title}</h3>
                <p className="text-gray-600 text-sm">Released: {movie.releaseDate}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default FrontPage;
