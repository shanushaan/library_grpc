import React from 'react';
import { NavLink } from 'react-router-dom';
import { BookOpen, ChevronLeft, ChevronRight } from 'lucide-react';
import clsx from 'clsx';

const Sidebar = ({ menuItems, collapsed, onToggle, userRole }) => {
  return (
    <div className={clsx('sidebar', { collapsed }, userRole)}>
      <div className="sidebar-header">
        <div className="logo">
          <BookOpen className="logo-icon" size={collapsed ? 24 : 32} />
          {!collapsed && (
            <div className="logo-text">
              <h2>Library</h2>
              <span>{userRole === 'admin' ? 'Admin Panel' : 'My Space'}</span>
            </div>
          )}
        </div>
        
        <button className="sidebar-toggle" onClick={onToggle}>
          {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      <nav className="sidebar-nav">
        <ul className="nav-list">
          {menuItems.map((item) => (
            <li key={item.id} className="nav-item">
              <NavLink
                to={item.path}
                className={({ isActive }) => 
                  clsx('nav-link', { active: isActive })
                }
                end={item.path === '/admin' || item.path === '/dashboard'}
              >
                <item.icon className="nav-icon" size={20} />
                {!collapsed && <span className="nav-label">{item.label}</span>}
                {collapsed && (
                  <div className="tooltip">
                    <span>{item.label}</span>
                  </div>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar-footer">
        {!collapsed && (
          <div className="sidebar-info">
            <p className="version">Version 1.0.0</p>
            <p className="copyright">© 2024 Library System</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;