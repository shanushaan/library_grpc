import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { removeNotification } from '../../store/slices/uiSlice';
import { X } from 'lucide-react';
import ErrorBoundary from './ErrorBoundary';
import '../../styles/Notifications.css';

const NotificationContainer = () => {
  const dispatch = useDispatch();
  const notifications = useSelector(state => state.ui.notifications);

  useEffect(() => {
    notifications.forEach(notification => {
      if (notification.autoHide) {
        const timer = setTimeout(() => {
          dispatch(removeNotification(notification.id));
        }, 5000);
        
        return () => clearTimeout(timer);
      }
    });
  }, [notifications, dispatch]);

  if (notifications.length === 0) return null;

  return (
    <ErrorBoundary fallbackMessage="Notification system error.">
      <div className="notification-container">
        {notifications.map(notification => (
          <div 
            key={notification.id} 
            className={`notification ${notification.type} ${notification.errorType || ''}`}
          >
            <span>{notification.message}</span>
            <button 
              onClick={() => dispatch(removeNotification(notification.id))}
              className="notification-close"
            >
              <X size={16} />
            </button>
          </div>
        ))}
      </div>
    </ErrorBoundary>
  );
};

export default NotificationContainer;