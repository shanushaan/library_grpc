import React, { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import ErrorBoundary from './ErrorBoundary';

const NotificationBell = ({ user }) => {
  const [notifications, setNotifications] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    if (!user?.user_id) return;
    
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8001';
    const ws = new WebSocket(`${wsUrl}?userId=${user.user_id}`);
    
    ws.onmessage = (event) => {
      const notification = JSON.parse(event.data);
      const newNotification = {
        id: Date.now(),
        message: notification.message,
        type: notification.type === 'REQUEST_APPROVED' ? 'success' : 'error',
        time: new Date().toLocaleDateString()
      };
      
      setNotifications(prev => [newNotification, ...prev.slice(0, 4)]);
      
      // Show toast notification
      showToast(newNotification);
    };

    return () => ws.close();
  }, [user]);
  
  const showToast = (notification) => {
    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      min-width: 300px;
      padding: 12px 16px;
      border-radius: 8px;
      color: white;
      font-size: 14px;
      z-index: 1002;
      background: ${notification.type === 'success' ? '#28a745' : '#dc3545'};
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    toast.textContent = notification.message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      if (toast.parentNode) {
        toast.remove();
      }
    }, 4000);
  };

  const unreadCount = notifications.length;

  return (
    <ErrorBoundary fallbackMessage="Notification system unavailable.">
      <div className="notification-bell">
        <button 
          className="bell-button"
          onClick={() => setShowDropdown(!showDropdown)}
        >
          <Bell size={20} />
          {unreadCount > 0 && (
            <span className="notification-badge">{unreadCount}</span>
          )}
        </button>

        {showDropdown && (
          <div className="notification-dropdown">
            <div className="notification-header">
              <h4>Notifications</h4>
            </div>
            <div className="notification-list">
              {notifications.length === 0 ? (
                <div className="no-notifications">No new notifications</div>
              ) : (
                notifications.map(notification => (
                  <div key={notification.id} className={`notification-item ${notification.type}`}>
                    <div className="notification-message">{notification.message}</div>
                    <div className="notification-time">{notification.time}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </ErrorBoundary>
  );
};

export default NotificationBell;