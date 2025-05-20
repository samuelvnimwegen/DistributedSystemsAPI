
import './App.css'
import FrontPage from "./components/FrontPage.tsx";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import {AuthProvider} from "./auth/AuthContext.tsx";
import PrivateRoute from "./auth/PrivateRoute.tsx";
import LoginPage from "./components/LoginPage.tsx";
import Dashboard from "./components/Dashboard.tsx";
import SignUpPage from "./components/SignUpPage.tsx";
import FriendsPage from "./components/FriendsPage.tsx";
import MoviePage from "./components/MoviePage.tsx";

function App() {

  return (
    <>
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<FrontPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
            <Route path="/movies/:movie_id" element={
              <PrivateRoute>
                <MoviePage />
              </PrivateRoute>
            } />
            <Route
                path="/friends"
                element={
                <PrivateRoute>
                    <FriendsPage />
                </PrivateRoute>
                }
            />
        </Routes>
      </Router>
    </AuthProvider>
    </>
  )
}

export default App
