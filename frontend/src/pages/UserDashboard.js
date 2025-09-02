import React from 'react';
import { Routes, Route } from 'react-router-dom';
import DashboardLayout from '../components/common/DashboardLayout';
import { userRoutes } from '../config/routes';
import { useAuth } from '../hooks/useAuth';

const UserDashboard = () => {
  const { user } = useAuth();

  return (
    <DashboardLayout menuItems={userRoutes} title="My Library" user={user}>
      <Routes>
        {userRoutes.map(route => {
          const Component = route.component;
          return (
            <Route 
              key={route.id}
              path={route.path.replace('/dashboard', '') || '/'}
              element={<Component user={user} />}
            />
          );
        })}
      </Routes>
    </DashboardLayout>
  );
};

export default UserDashboard;