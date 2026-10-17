import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import './Navbar.css';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">🌾 BioResidue</Link>

      <div className="nav-links">
        {user ? (
          <>
            <Link to="/browse" className={`nav-link ${isActive('/browse')}`}>Browse</Link>
            {user.role === 'farmer' && (
              <Link to="/list-residue" className={`nav-link ${isActive('/list-residue')}`}>List Residue</Link>
            )}
            <Link to="/dashboard" className={`nav-link ${isActive('/dashboard')}`}>Dashboard</Link>
            <div className="nav-user">
              <span className="nav-username">{user.username}</span>
              <span className={`nav-role ${user.role}`}>{user.role}</span>
            </div>
            <button id="logout-btn" onClick={handleLogout} className="nav-logout">Logout</button>
          </>
        ) : (
          <>
            <Link to="/login" className={`nav-link ${isActive('/login')}`}>Login</Link>
            <Link to="/register" className="nav-cta">Get Started</Link>
          </>
        )}
      </div>
    </nav>
  );
}
