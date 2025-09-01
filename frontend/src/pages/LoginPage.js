import React, { useState } from 'react';
import { BookOpen, User, Lock, Eye, EyeOff } from 'lucide-react';
import axios from 'axios';

const LoginPage = ({ onLogin }) => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('http://localhost:8001/login', credentials);
      onLogin(response.data);
    } catch (err) {
      setError('Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = (role) => {
    const demoCredentials = role === 'admin' 
      ? { username: 'admin', password: 'admin123' }
      : { username: 'john_user', password: 'user123' };
    
    setCredentials(demoCredentials);
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="floating-books">
          <BookOpen className="book-icon book-1" />
          <BookOpen className="book-icon book-2" />
          <BookOpen className="book-icon book-3" />
        </div>
      </div>
      
      <div className="login-card">
        <div className="login-header">
          <div className="logo">
            <BookOpen size={48} className="logo-icon" />
            <h1>Library Management</h1>
          </div>
          <p className="subtitle">Welcome back! Please sign in to continue</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <div className="input-wrapper">
              <User className="input-icon" size={20} />
              <input
                id="username"
                type="text"
                value={credentials.username}
                onChange={(e) => setCredentials({...credentials, username: e.target.value})}
                placeholder="Enter your username"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <Lock className="input-icon" size={20} />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={credentials.password}
                onChange={(e) => setCredentials({...credentials, password: e.target.value})}
                placeholder="Enter your password"
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="demo-section">
          <p className="demo-text">Try demo accounts:</p>
          <div className="demo-buttons">
            <button 
              onClick={() => handleDemoLogin('admin')} 
              className="demo-button admin"
            >
              Admin Demo
            </button>
            <button 
              onClick={() => handleDemoLogin('user')} 
              className="demo-button user"
            >
              User Demo
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;