import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider, useDispatch } from 'react-redux';
import { store } from './store';
import { AuthProvider, useAuth } from './hooks/useAuth';
import { fetchBookRequests } from './store/slices/bookRequestsSlice';
import { lazy, Suspense } from 'react';
import LoginPage from './pages/LoginPage';
import LoadingScreen from './components/common/LoadingScreen';

// Lazy load dashboard components
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'));
const UserDashboard = lazy(() => import('./pages/UserDashboard'));
import ProtectedRoute from './components/common/ProtectedRoute';
import NotificationContainer from './components/common/NotificationContainer';
import ErrorBoundary from './components/common/ErrorBoundary';
import './styles/App.css';
import './styles/UserDashboard.css';
import './styles/Notifications.css';

const AppRoutes = () => {
  const { user, loading } = useAuth();
  const dispatch = useDispatch();

  useEffect(() => {
    if (user?.role === 'ADMIN') {
      dispatch(fetchBookRequests());
    }
  }, [user, dispatch]);

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <Routes>
      <Route 
        path="/login" 
        element={
          user ? (
            <Navigate to={user.role === 'ADMIN' ? '/admin' : '/dashboard'} replace />
          ) : (
            <LoginPage />
          )
        } 
      />
      <Route 
        path="/admin/*" 
        element={
          <ProtectedRoute requiredRole="ADMIN">
            <ErrorBoundary fallbackMessage="Admin dashboard encountered an error.">
              <Suspense fallback={<LoadingScreen />}>
                <AdminDashboard />
              </Suspense>
            </ErrorBoundary>
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/dashboard/*" 
        element={
          <ProtectedRoute requiredRole="USER">
            <ErrorBoundary fallbackMessage="User dashboard encountered an error.">
              <Suspense fallback={<LoadingScreen />}>
                <UserDashboard />
              </Suspense>
            </ErrorBoundary>
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/" 
        element={
          user ? (
            <Navigate to={user.role === 'ADMIN' ? '/admin' : '/dashboard'} replace />
          ) : (
            <Navigate to="/login" replace />
          )
        } 
      />
    </Routes>
  );
};

function App() {
  return (
    <ErrorBoundary fallbackMessage="Application crashed. Please refresh the page.">
      <Provider store={store}>
        <AuthProvider>
          <Router>
            <div className="App">
              <AppRoutes />
              <NotificationContainer />
            </div>
          </Router>
        </AuthProvider>
      </Provider>
    </ErrorBoundary>
  );
}

export default App;