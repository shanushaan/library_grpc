import React, { useState } from 'react';
import Sidebar from '../Sidebar';
import Header from '../Header';
import NotificationBell from './NotificationBell';
import { useAuth } from '../../hooks/useAuth';

const DashboardLayout = ({ menuItems, title, children, user: propUser }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { user: authUser, logout } = useAuth();
  const user = propUser || authUser;

  return (
    <div className={`dashboard-layout ${user?.role?.toLowerCase()}-dashboard`}>
      <Sidebar 
        menuItems={menuItems}
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        userRole={user?.role?.toLowerCase()}
      />
      
      <div className={`main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
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