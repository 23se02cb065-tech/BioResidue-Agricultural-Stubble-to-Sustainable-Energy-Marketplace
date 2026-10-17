import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import './Auth.css';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', email: '', password: '', role: 'farmer' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await register(form);
      navigate(user.role === 'farmer' ? '/list-residue' : '/browse');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">🌱</div>
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-subtitle">Join the BioResidue Marketplace</p>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="role-toggle">
            <button
              id="role-farmer"
              type="button"
              className={`role-btn ${form.role === 'farmer' ? 'active' : ''}`}
              onClick={() => setForm({ ...form, role: 'farmer' })}
            >
              🌾 I am a Farmer
            </button>
            <button
              id="role-company"
              type="button"
              className={`role-btn ${form.role === 'company' ? 'active' : ''}`}
              onClick={() => setForm({ ...form, role: 'company' })}
            >
              🏭 I am a Company
            </button>
          </div>

          <div className="form-group">
            <label>Username</label>
            <input
              id="reg-username"
              type="text"
              value={form.username}
              onChange={e => setForm({ ...form, username: e.target.value })}
              placeholder="Choose a username"
              required
            />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input
              id="reg-email"
              type="email"
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              placeholder="Your email address"
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              id="reg-password"
              type="password"
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              placeholder="Create a password"
              required
            />
          </div>

          <button id="reg-submit" type="submit" className="auth-btn" disabled={loading}>
            {loading ? 'Creating Account…' : 'Create Account'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in here</Link>
        </p>
      </div>
    </div>
  );
}
