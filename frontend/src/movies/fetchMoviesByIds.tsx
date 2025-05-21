export const fetchMoviesByIds = async (movieIds: number[]) => {
    if (movieIds.length === 0) return [];

    try {
        const params = movieIds.map(id => `movie_ids=${id}`).join('&');
        const response = await fetch(`http://localhost/api/movies/list?${params}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error('Failed to fetch movies');
        }

        const data = await response.json();
        return data.results || data; // Adjust this depending on your API response shape
    } catch (error) {
        console.error('Error fetching movies:', error);
        return [];
    }
};
