import React, { useState } from 'react';
import { LogOut, User } from 'lucide-react';
import '../styles/Header.css';

const Header = ({ user, onLogout, title }) => {
  const [showUserMenu, setShowUserMenu] = useState(false);

  return (
    <header className="dashboard-header">
      <div className="header-left">
        <h1 className="page-title">{title}</h1>
      </div>

      <div className="header-right">
        <div className="user-section">
          <span className="user-welcome">Welcome, {user.username}</span>
          
          <div className="user-menu">
            <button 
              className="user-button"
              onClick={() => setShowUserMenu(!showUserMenu)}
            >
              <User size={18} />
              <span className="user-role">{user.role}</span>
            </button>

            {showUserMenu && (
              <div className="user-dropdown">
                <div className="user-info">
                  <strong>{user.username}</strong>
                  <span>{user.email}</span>
                </div>
                <button className="logout-button" onClick={onLogout}>
                  <LogOut size={16} />
                  Sign Out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;