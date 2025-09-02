import React, { useState, useEffect, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Search, Calendar, User, Book, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import { fetchTransactions } from '../../store/slices/transactionsSlice';
import '../../styles/TransactionsManagement.css';

const TransactionsManagement = () => {
  const dispatch = useDispatch();
  const { data: transactions, loading, currentPage, totalPages, totalCount, limit } = useSelector(state => state.transactions);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');

  const loadTransactions = (page = 1) => {
    dispatch(fetchTransactions({ status: selectedStatus, page, limit }));
  };

  useEffect(() => {
    loadTransactions(1);
  }, [selectedStatus, dispatch]);

  useEffect(() => {
    loadTransactions(currentPage);
  }, [currentPage, dispatch]);

  const filteredTransactions = useMemo(() => {
    if (!Array.isArray(transactions)) return [];
    return transactions.filter(txn => {
      const matchesSearch = txn.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           txn.book_title.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesSearch;
    });
  }, [transactions, searchQuery]);

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'BORROWED': return 'borrowed';
      case 'RETURNED': return 'returned';
      case 'OVERDUE': return 'overdue';
      default: return 'unknown';
    }
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Transactions Management</h2>
        
        <div className="filters-section">
          <div className="search-box">
            <Search size={20} />
            <input
              type="text"
              placeholder="Search by user or book..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <select 
            value={selectedStatus} 
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="filter-select"
          >
            <option value="">All Status</option>
            <option value="BORROWED">Borrowed</option>
            <option value="RETURNED">Returned</option>
            <option value="OVERDUE">Overdue</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading transactions...</p>
        </div>
      ) : (
        <div className="transactions-table-container">
          <table className="transactions-table">
            <thead>
              <tr>
                <th>Transaction ID</th>
                <th>User</th>
                <th>Book</th>
                <th>Type</th>
                <th>Borrowed Date</th>
                <th>Due Date</th>
                <th>Return Date</th>
                <th>Status</th>
                <th>Fine</th>
              </tr>
            </thead>
            <tbody>
              {filteredTransactions.map(txn => (
                <tr key={txn.transaction_id}>
                  <td className="transaction-id-cell">#{txn.transaction_id}</td>
                  <td>
                    <div className="user-info">
                      <User size={14} />
                      {txn.username}
                    </div>
                  </td>
                  <td>
                    <div className="book-info">
                      <Book size={14} />
                      {txn.book_title}
                    </div>
                  </td>
                  <td>
                    <span className="type-badge">
                      {txn.transaction_type}
                    </span>
                  </td>
                  <td>{formatDate(txn.transaction_date)}</td>
                  <td>{formatDate(txn.due_date)}</td>
                  <td>{formatDate(txn.return_date)}</td>
                  <td>
                    <span className={`status-badge ${getStatusColor(txn.status)}`}>
                      {txn.status}
                    </span>
                  </td>
                  <td>
                    {txn.fine_amount > 0 ? (
                      <span className="fine-amount">${txn.fine_amount}</span>
                    ) : (
                      <span className="no-fine">$0</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && filteredTransactions.length === 0 && (
        <div className="no-results">
          <Calendar size={48} />
          <h3>No transactions found</h3>
          <p>Try adjusting your search terms or filters</p>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination">
          <button 
            className="pagination-btn" 
            onClick={() => loadTransactions(Math.max(currentPage - 1, 1))}
            disabled={currentPage === 1}
          >
            <ChevronLeft size={16} />
            Previous
          </button>
          
          <div className="pagination-info">
            <span>Page {currentPage} of {totalPages}</span>
            <span className="pagination-count">({totalCount} total transactions)</span>
          </div>
          
          <button 
            className="pagination-btn" 
            onClick={() => loadTransactions(Math.min(currentPage + 1, totalPages))}
            disabled={currentPage === totalPages}
          >
            Next
            <ChevronRight size={16} />
          </button>
        </div>
      )}
    </div>
  );
};

export default TransactionsManagement;