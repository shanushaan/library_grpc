import React, { useState, useEffect } from 'react';
import { Menu, X } from 'lucide-react';
import Sidebar from '../Sidebar';
import Header from '../Header';
import NotificationBell from './NotificationBell';
import { useAuth } from '../../hooks/useAuth';

const DashboardLayout = ({ menuItems, title, children, user: propUser }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const { user: authUser, logout } = useAuth();
  const user = propUser || authUser;

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth <= 768;
      setIsMobile(mobile);
      if (!mobile) {
        setMobileMenuOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className={`dashboard-layout ${user?.role?.toLowerCase()}-dashboard`}>
      {/* Mobile Menu Button */}
      {isMobile && (
        <button 
          className="mobile-menu-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      )}

      {/* Mobile Overlay */}
      {isMobile && mobileMenuOpen && (
        <div 
          className="mobile-overlay"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      <Sidebar 
        menuItems={menuItems}
        collapsed={isMobile ? false : sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        userRole={user?.role?.toLowerCase()}
        isMobile={isMobile}
        mobileMenuOpen={mobileMenuOpen}
        onMobileClose={() => setMobileMenuOpen(false)}
      />
      
      <div className={`main-content ${!isMobile && sidebarCollapsed ? 'sidebar-collapsed' : ''} ${isMobile ? 'mobile' : ''}`}>
        <Header 
          user={user}
          onLogout={logout}
          title={title}
        />
        
        {user?.role === 'USER' && (
          <div className="notification-bell-container">
            <NotificationBell user={user} />
          </div>
        )}
        
        <div className="content-area">
          {children}
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout;