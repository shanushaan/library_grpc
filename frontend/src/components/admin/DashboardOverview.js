import React, { useEffect } from 'react';
import { BookOpen, Users, Receipt, AlertCircle } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchUsers } from '../../store/slices/usersSlice';
import { fetchBooks } from '../../store/slices/booksSlice';
import { fetchTransactions } from '../../store/slices/transactionsSlice';
import StatCard from '../common/StatCard';

const DashboardOverview = () => {
  const dispatch = useDispatch();
  const { data: users, loading: usersLoading } = useSelector(state => state.users);
  const { data: books, loading: booksLoading } = useSelector(state => state.books);
  const { data: transactions, loading: transactionsLoading } = useSelector(state => state.transactions);
  
  const loading = usersLoading || booksLoading || transactionsLoading;
  
  const stats = {
    totalBooks: books.length,
    activeUsers: users.filter(u => u.is_active).length,
    borrowedBooks: transactions.filter(t => t.status === 'BORROWED').length,
    overdueBooks: transactions.filter(t => 
      t.status === 'BORROWED' && new Date(t.due_date) < new Date()
    ).length
  };

  useEffect(() => {
    dispatch(fetchUsers());
    dispatch(fetchBooks());
    dispatch(fetchTransactions());
  }, [dispatch]);

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
            <StatCard
              key={index}
              label={stat.label}
              value={stat.value}
              icon={stat.icon}
              color={stat.color}
            />
          ))
        )}
      </div>


    </div>
  );
};

export default DashboardOverview;