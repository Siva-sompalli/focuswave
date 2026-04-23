import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import About from './pages/About'; // You need to create a simple About.jsx
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Prediction from './pages/Prediction';
import Result from './pages/Result';
import Emotion from './pages/Emotion';

// ⚠️ PrivateRoute Component: Protects routes that require login
const PrivateRoute = ({ children }) => {
  const isAuthenticated = localStorage.getItem('authToken'); // Check for stored token
  return isAuthenticated ? children : <Navigate to="/login" />;
};

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Public Routes (Pre-Login) */}
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} /> 
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Private Routes (Post-Login) */}
        <Route 
          path="/dashboard" 
          element={<PrivateRoute><Dashboard /></PrivateRoute>} 
        />
        <Route 
          path="/tasks" 
          element={<PrivateRoute><Tasks /></PrivateRoute>} 
        />
        <Route 
          path="/prediction" 
          element={<PrivateRoute><Prediction /></PrivateRoute>} 
        />
        <Route 
          path="/result" 
          element={<PrivateRoute><Result /></PrivateRoute>} 
        />
        <Route 
          path="/emotion" 
          element={<PrivateRoute><Emotion /></PrivateRoute>} 
        />
        
        {/* Fallback Route */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
};

export default App;

// You still need to create a simple `src/pages/About.jsx`
// or the application will throw an error when navigating to /about.
// For now, assume it's a simple placeholder:

/*
// src/pages/About.jsx
import React from 'react';
import Navbar from '../components/Navbar';
const About = () => (
    <>
        <Navbar />
        <div style={{ padding: '50px', textAlign: 'center' }}>
            <h1>ℹ️ About FocusWave</h1>
            <p>FocusWave is designed to help individuals, especially those with ADHD, manage their focus and productivity using personalized, machine-learning-driven Pomodoro cycles.</p>
        </div>
    </>
);
export default About;
*/