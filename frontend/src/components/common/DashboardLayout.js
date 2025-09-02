import React, { useState } from 'react';
import Sidebar from '../Sidebar';
import Header from '../Header';
import { useAuth } from '../../contexts/AuthContext';

const DashboardLayout = ({ menuItems, title, children }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { user, logout } = useAuth();

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
        
        <div className="content-area">
          {children}
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout;