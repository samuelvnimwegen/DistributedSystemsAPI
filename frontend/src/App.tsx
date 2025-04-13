
import './App.css'
import FrontPage from "./components/FrontPage.tsx";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import {AuthProvider} from "./auth/AuthContext.tsx";
import PrivateRoute from "./auth/PrivateRoute.tsx";
import LoginPage from "./components/LoginPage.tsx";
import Dashboard from "./components/Dashboard.tsx";

function App() {

  return (
    <>
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<FrontPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
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
