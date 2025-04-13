import React from 'react';
import { useAuth } from '../auth/AuthContext';
import { useNavigate } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold">🎉 Welcome to Your Dashboard</h1>
        <button
          onClick={handleLogout}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
        >
          Logout
        </button>
      </div>

      <div className="grid gap-6 md:grid-cols-3 mb-8">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-2">Watched Movies</h2>
          <p className="text-2xl font-bold text-blue-600">14</p>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-2">Favorites</h2>
          <p className="text-2xl font-bold text-purple-600">5</p>
        </div>
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-2">Reviews</h2>
          <p className="text-2xl font-bold text-green-600">3</p>
        </div>
      </div>

      <section>
        <h2 className="text-2xl font-bold mb-4">Quick Links</h2>
        <ul className="list-disc pl-6 space-y-2 text-blue-600">
          <li>
            <a href="/movies">Browse Movies</a>
          </li>
          <li>
            <a href="/favorites">View Favorites</a>
          </li>
          <li>
            <a href="/reviews">Your Reviews</a>
          </li>
        </ul>
      </section>
    </div>
  );
};

export default Dashboard;
