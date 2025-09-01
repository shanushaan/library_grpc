import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import UserOverview from '../components/user/UserOverview';
import BookCatalog from '../components/user/BookCatalog';
import MyBooks from '../components/user/MyBooks';
import BookHistory from '../components/user/BookHistory';
import UserProfile from '../components/user/UserProfile';
import { 
  LayoutDashboard, 
  Search, 
  BookOpen, 
  History,
  User
} from 'lucide-react';

const UserDashboard = ({ user, onLogout }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const userMenuItems = [
    { 
      id: 'overview', 
      label: 'Dashboard', 
      icon: LayoutDashboard, 
      path: '/dashboard',
      component: () => <UserOverview user={user} />
    },
    { 
      id: 'catalog', 
      label: 'Browse Books', 
      icon: Search, 
      path: '/dashboard/catalog',
      component: () => <BookCatalog user={user} />
    },
    { 
      id: 'my-books', 
      label: 'My Books', 
      icon: BookOpen, 
      path: '/dashboard/my-books',
      component: () => <MyBooks user={user} />
    },
    { 
      id: 'history', 
      label: 'Reading History', 
      icon: History, 
      path: '/dashboard/history',
      component: BookHistory 
    },
    { 
      id: 'profile', 
      label: 'My Profile', 
      icon: User, 
      path: '/dashboard/profile',
      component: UserProfile 
    }
  ];

  return (
    <div className="dashboard-layout user-dashboard">
      <Sidebar 
        menuItems={userMenuItems}
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        userRole="user"
      />
      
      <div className={`main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
        <Header 
          user={user}
          onLogout={onLogout}
          title="My Library"
        />
        
        <div className="content-area">
          <Routes>
            {userMenuItems.map(item => (
              <Route 
                key={item.id}
                path={item.path.replace('/dashboard', '') || '/'}
                element={<item.component />}
              />
            ))}
          </Routes>
        </div>
      </div>
    </div>
  );
};

export default UserDashboard;