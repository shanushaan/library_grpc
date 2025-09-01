import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import DashboardOverview from '../components/admin/DashboardOverview';
import BooksManagement from '../components/admin/BooksManagement';
import BookRequests from '../components/admin/BookRequests';
import UsersManagement from '../components/admin/UsersManagement';
import TransactionsManagement from '../components/admin/TransactionsManagement';
import ReportsAnalytics from '../components/admin/ReportsAnalytics';
import { 
  LayoutDashboard, 
  BookOpen, 
  Users, 
  Receipt, 
  BarChart3,
  Settings,
  FileText
} from 'lucide-react';

const AdminDashboard = ({ user, onLogout }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const adminMenuItems = [
    { 
      id: 'overview', 
      label: 'Librarian Dashboard', 
      icon: LayoutDashboard, 
      path: '/admin',
      component: DashboardOverview 
    },
    { 
      id: 'books', 
      label: 'Librarian Books', 
      icon: BookOpen, 
      path: '/admin/books',
      component: BooksManagement 
    },
    { 
      id: 'requests', 
      label: 'Book Requests', 
      icon: FileText, 
      path: '/admin/requests',
      component: BookRequests 
    },
    { 
      id: 'users', 
      label: 'Library Users', 
      icon: Users, 
      path: '/admin/users',
      component: UsersManagement 
    },
    { 
      id: 'transactions', 
      label: 'Transactions', 
      icon: Receipt, 
      path: '/admin/transactions',
      component: TransactionsManagement 
    },
    { 
      id: 'reports', 
      label: 'Reports & Analytics', 
      icon: BarChart3, 
      path: '/admin/reports',
      component: ReportsAnalytics 
    },
    { 
      id: 'settings', 
      label: 'Settings', 
      icon: Settings, 
      path: '/admin/settings',
      component: () => <div className="page-content">Settings Page</div>
    }
  ];

  return (
    <div className="dashboard-layout admin-dashboard">
      <Sidebar 
        menuItems={adminMenuItems}
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        userRole="admin"
      />
      
      <div className={`main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <Header 
          user={user}
          onLogout={onLogout}
          title="Librarian Dashboard"
        />
        
        <div className="content-area">
          <Routes>
            {adminMenuItems.map(item => (
              <Route 
                key={item.id}
                path={item.path.replace('/admin', '') || '/'}
                element={<item.component />}
              />
            ))}
          </Routes>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;