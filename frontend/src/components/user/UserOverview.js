import React, { useState, useEffect } from 'react';
import { BookOpen, Clock, AlertTriangle, DollarSign } from 'lucide-react';
import axios from 'axios';
import { API_CONFIG } from '../../config/api';

const UserOverview = ({ user }) => {
  const [stats, setStats] = useState({
    total_books_taken: 0,
    currently_borrowed: 0,
    overdue_books: 0,
    total_fine: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(API_CONFIG.getVersionedUrl(`/user/${user.user_id}/stats`));
        setStats(response.data);
      } catch (error) {
        console.error('Error fetching user stats:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user?.user_id) {
      fetchStats();
    }
  }, [user]);

  if (loading) {
    return <div className="page-content">Loading...</div>;
  }

  return (
    <div className="page-content user-overview">
      <div className="welcome-section">
        <h2>Welcome back, {user?.username}!</h2>
        <p>Continue your reading journey</p>
      </div>

      <div className="user-stats">
        <div className="stat-card">
          <BookOpen className="stat-icon" />
          <div className="stat-info">
            <h3>{stats.total_books_taken}</h3>
            <p>Total Books Taken</p>
          </div>
        </div>
        <div className="stat-card">
          <Clock className="stat-icon" />
          <div className="stat-info">
            <h3>{stats.currently_borrowed}</h3>
            <p>Currently Borrowed</p>
          </div>
        </div>
        <div className="stat-card">
          <AlertTriangle className="stat-icon" style={{ color: stats.overdue_books > 0 ? '#f59e0b' : '#6b7280' }} />
          <div className="stat-info">
            <h3>{stats.overdue_books}</h3>
            <p>Overdue Books</p>
          </div>
        </div>
        <div className="stat-card">
          <DollarSign className="stat-icon" style={{ color: stats.total_fine > 0 ? '#ef4444' : '#6b7280' }} />
          <div className="stat-info">
            <h3>${stats.total_fine}</h3>
            <p>Total Fine</p>
          </div>
        </div>
      </div>

      {stats.overdue_books > 0 && (
        <div className="alert alert-warning">
          <AlertTriangle size={20} />
          <span>You have {stats.overdue_books} overdue book(s) with a total fine of ${stats.total_fine}. Please return them soon!</span>
        </div>
      )}
    </div>
  );
};

export default UserOverview;