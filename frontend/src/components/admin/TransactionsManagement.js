import React, { useState, useEffect, useMemo } from 'react';
import { Search, Calendar, User, Book, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import '../../styles/TransactionsManagement.css';

const TransactionsManagement = () => {
  const [transactions, setTransactions] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [limit] = useState(20);

  const fetchTransactions = async (page = 1) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8001/api/v1/admin/transactions?status=${selectedStatus}&page=${page}&limit=${limit}`);
      const data = await response.json();
      
      // Ensure transactions is always an array
      const transactionsArray = Array.isArray(data.transactions) ? data.transactions : 
                               Array.isArray(data) ? data : [];
      
      setTransactions(transactionsArray);
      setCurrentPage(data.page || page);
      setTotalPages(data.total_pages || 1);
      setTotalCount(data.total_count || transactionsArray.length);
    } catch (error) {
      console.error('Error fetching transactions:', error);
      setTransactions([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setCurrentPage(1);
    fetchTransactions(1);
  }, [selectedStatus]);

  useEffect(() => {
    fetchTransactions(currentPage);
  }, [currentPage]);

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
            onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
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
            onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
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