import React from 'react';
import { Routes, Route } from 'react-router-dom';
import DashboardLayout from '../components/common/DashboardLayout';
import { adminRoutes } from '../config/routes';

const AdminDashboard = () => {
  return (
    <DashboardLayout menuItems={adminRoutes} title="Librarian Dashboard">
      <Routes>
        {adminRoutes.map(route => (
          <Route 
            key={route.id}
            path={route.path.replace('/admin', '') || '/'}
            element={<route.component />}
          />
        ))}
      </Routes>
    </DashboardLayout>
  );
};

export default AdminDashboard;