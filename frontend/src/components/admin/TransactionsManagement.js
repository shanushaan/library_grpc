import React, { useState, useEffect, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Calendar, User, Book, ChevronLeft, ChevronRight } from 'lucide-react';
import { fetchTransactions } from '../../store/slices/transactionsSlice';
import EnhancedDataTable from '../common/EnhancedDataTable';
import '../../styles/TransactionsManagement.css';

const TransactionsManagement = () => {
  const dispatch = useDispatch();
  const { data: transactions, loading, currentPage, totalPages, totalCount, limit } = useSelector(state => state.transactions);
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
      </div>

      <EnhancedDataTable
        data={Array.isArray(transactions) ? transactions : []}
        columns={[
          { key: 'transaction_id', header: 'Transaction ID', render: (value) => <span className="transaction-id-cell">#{value}</span> },
          { key: 'username', header: 'User', render: (value) => (
            <div className="user-info">
              <User size={14} />
              {value}
            </div>
          )},
          { key: 'book_title', header: 'Book', render: (value) => (
            <div className="book-info">
              <Book size={14} />
              {value}
            </div>
          )},
          { key: 'transaction_type', header: 'Type', render: (value) => <span className="type-badge">{value}</span> },
          { key: 'transaction_date', header: 'Borrowed Date', render: (value) => formatDate(value) },
          { key: 'due_date', header: 'Due Date', render: (value) => formatDate(value) },
          { key: 'return_date', header: 'Return Date', render: (value) => formatDate(value) },
          { key: 'status', header: 'Status', render: (value) => (
            <span className={`status-badge ${getStatusColor(value)}`}>
              {value}
            </span>
          )},
          { key: 'fine_amount', header: 'Fine', render: (value) => (
            value > 0 ? (
              <span className="fine-amount">${value}</span>
            ) : (
              <span className="no-fine">$0</span>
            )
          )}
        ]}
        keyField="transaction_id"
        searchable={true}
        searchPlaceholder="Search by user or book..."
        filters={[
          { value: 'BORROWED', label: 'Borrowed', filter: (txn) => txn.status === 'BORROWED' },
          { value: 'RETURNED', label: 'Returned', filter: (txn) => txn.status === 'RETURNED' },
          { value: 'OVERDUE', label: 'Overdue', filter: (txn) => txn.status === 'OVERDUE' }
        ]}
        emptyMessage={loading ? "Loading transactions..." : "No transactions found"}
        className="transactions-table"
      />

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