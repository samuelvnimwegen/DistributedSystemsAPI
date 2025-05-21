import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import "../css/FrontPage.css"
import "../css/Login.css"
import {useState} from "react";

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

    const handleSignup = async () => {
      try {
        const response = await fetch('/api/users/sign_up', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ username, password }), // assuming you have those in state
        });

        if (response.ok) {
          login();
          navigate('/dashboard');
        } else {
          const error = await response.json();
          alert(error.message || 'Login failed');
        }
      } catch (err) {
        console.error(err);
        alert('An error occurred during login');
      }
    };

  const handleHomeClick = () => {
    navigate('/'); // Redirect to the home page
  }
    const handleLoginRedirect = () => {
        navigate('/login'); // Redirect to the signup page
    };

  return (
    <div className="p-6">
      <header className="top-bar">
        <button
          onClick={handleHomeClick}
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
          Home
        </button>
        <h1 className="top-bar-title">NextFilm</h1>
      </header>

        {/* Login Form */}
         <div className="login-page">
      <div className="login-box">
        <h1 className="login-title">Sign Up</h1>

        <form onSubmit={(e) => e.preventDefault()}>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your username"
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
          />

          <button type="button" onClick={handleSignup}>
            Sign Up
          </button>
        </form>

        <div className="signup-link">
          <p>Already have an account? <span onClick={handleLoginRedirect}>Log in</span></p>
        </div>
      </div>
</div>
    </div>
  );
};

export default LoginPage;
