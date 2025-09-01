import React, { useState, useEffect } from 'react';
import { BookOpen, Users, Receipt, AlertCircle } from 'lucide-react';
import axios from 'axios';

const DashboardOverview = () => {
  const [stats, setStats] = useState({
    totalBooks: 0,
    activeUsers: 0,
    borrowedBooks: 0,
    overdueBooks: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [booksResponse, usersResponse, statsResponse] = await Promise.all([
          axios.get('http://localhost:8001/admin/books'),
          axios.get('http://localhost:8001/admin/users'),
          axios.get('http://localhost:8001/admin/stats')
        ]);
        
        setStats({
          totalBooks: Array.isArray(booksResponse.data) ? booksResponse.data.length : 0,
          activeUsers: Array.isArray(usersResponse.data) ? usersResponse.data.filter(u => u.is_active).length : 0,
          borrowedBooks: statsResponse.data.borrowed_books || 0,
          overdueBooks: statsResponse.data.overdue_books || 0
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
        setStats({
          totalBooks: 0,
          activeUsers: 0,
          borrowedBooks: 0,
          overdueBooks: 0
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const statCards = [
    { label: 'Total Books', value: stats.totalBooks, icon: BookOpen, color: 'blue' },
    { label: 'Active Users', value: stats.activeUsers, icon: Users, color: 'green' },
    { label: 'Books Borrowed', value: stats.borrowedBooks, icon: Receipt, color: 'purple' },
    { label: 'Overdue Books', value: stats.overdueBooks, icon: AlertCircle, color: 'red' }
  ];

  const recentActivities = [
    { id: 1, action: 'New book added', details: '"The Art of Programming" by John Doe', time: '2 min ago', type: 'success' },
    { id: 2, action: 'Member registered', details: 'Sarah Johnson joined the library', time: '15 min ago', type: 'info' },
    { id: 3, action: 'Book returned', details: '"Clean Code" returned by Mike Brown', time: '1 hour ago', type: 'success' },
    { id: 4, action: 'Overdue notice', details: '"React Patterns" is 3 days overdue', time: '2 hours ago', type: 'warning' }
  ];

  return (
    <div className="page-content dashboard-overview">
      <div className="page-header">
        <h2>Librarian Dashboard</h2>
        <p>Welcome back! Here's what's happening in your library today.</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        {loading ? (
          <div>Loading stats...</div>
        ) : (
          statCards.map((stat, index) => (
            <div key={index} className={`stat-card ${stat.color}`}>
              <div className="stat-icon">
                <stat.icon size={24} />
              </div>
              <div className="stat-content">
                <h3 className="stat-value">{stat.value}</h3>
                <p className="stat-label">{stat.label}</p>
              </div>
            </div>
          ))
        )}
      </div>


    </div>
  );
};

export default DashboardOverview;