import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useDispatch } from 'react-redux';
import { Calendar, User, BookOpen, Clock, AlertTriangle } from 'lucide-react';
import { showNotification } from '../../store/slices/uiSlice';
import { incrementPendingCount } from '../../store/slices/bookRequestsSlice';
import { transactionValidation } from '../../utils/validationSchemas';
import { handleApiError } from '../../utils/errorHandler';
import ErrorBoundary from '../common/ErrorBoundary';
import DataTable from '../common/DataTable';
import { API_CONFIG } from '../../config/api';

const MyBooks = ({ user }) => {
  const dispatch = useDispatch();
  const [borrowedBooks, setBorrowedBooks] = useState([]);
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchMyBooks = async () => {
    setLoading(true);
    try {
      const [requestsResponse, transactionsResponse] = await Promise.all([
        axios.get(API_CONFIG.getVersionedUrl(`/user/${user.user_id}/book-requests`)),
        axios.get(API_CONFIG.getVersionedUrl(`/user/${user.user_id}/transactions?status=BORROWED`))
      ]);
      
      setBorrowedBooks(transactionsResponse.data);
      setRequests(requestsResponse.data);
    } catch (error) {
      handleApiError(error, dispatch, showNotification);
    } finally {
      setLoading(false);
    }
  };

  const requestReturn = async (transactionId, bookTitle, bookId) => {
    // Validate return eligibility
    const returnError = transactionValidation.validateReturnEligibility(borrowedBooks, bookId);
    if (returnError) {
      dispatch(showNotification({ message: returnError, type: 'error' }));
      return;
    }
    
    // Check if return request already exists
    const existingReturnRequest = requests.find(req => 
      req.transaction_id === transactionId && 
      req.request_type === 'RETURN' && 
      req.status === 'PENDING'
    );
    
    if (existingReturnRequest) {
      dispatch(showNotification({ message: 'Return request already submitted for this book', type: 'error' }));
      return;
    }
    
    try {
      const response = await axios.post(API_CONFIG.getVersionedUrl('/user/book-request'), {
        book_id: bookId,
        request_type: 'RETURN',
        user_id: user.user_id,
        transaction_id: transactionId,
        notes: `Return request for ${bookTitle}`
      });
      
      dispatch(showNotification({ message: response.data.message, type: 'success' }));
      dispatch(incrementPendingCount());
      fetchMyBooks();
    } catch (error) {
      handleApiError(error, dispatch, showNotification);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const isOverdue = (dueDateString) => {
    if (!dueDateString) return false;
    return new Date(dueDateString) < new Date();
  };

  useEffect(() => {
    if (user?.user_id) {
      fetchMyBooks();
    }
  }, [user]);

  if (loading) return <div className="page-content">Loading...</div>;

  return (
    <ErrorBoundary fallbackMessage="My books section unavailable.">
      <div className="page-content my-books">
        <h2>My Books</h2>

        <div className="section">
          <h3>Currently Borrowed Books</h3>
          <DataTable
            data={borrowedBooks}
            columns={[
              { key: 'book_title', header: 'Book', render: (value, book) => (
                <div className="book-info">
                  <strong>{value}</strong>
                  {isOverdue(book.due_date) && <AlertTriangle size={16} className="overdue-icon" />}
                </div>
              )},
              { key: 'book_author', header: 'Author' },
              { key: 'transaction_date', header: 'Borrowed Date', render: (value) => (
                <div className="date-info">
                  <Calendar size={14} />
                  {formatDate(value)}
                </div>
              )},
              { key: 'due_date', header: 'Due Date', render: (value) => (
                <div className={`date-info ${isOverdue(value) ? 'overdue' : ''}`}>
                  <Clock size={14} />
                  {formatDate(value)}
                </div>
              )},
              { key: 'fine_amount', header: 'Fine', render: (value) => (
                <span className={`fine-amount ${value > 0 ? 'has-fine' : ''}`}>
                  ${value || 0}
                </span>
              )},
              { key: 'actions', header: 'Actions', render: (_, book) => {
                const hasReturnRequest = requests.some(req => 
                  req.transaction_id === book.transaction_id && 
                  req.request_type === 'RETURN' && 
                  req.status === 'PENDING'
                );
                
                return (
                  <button 
                    onClick={() => requestReturn(book.transaction_id, book.book_title, book.book_id)}
                    disabled={hasReturnRequest}
                    className={`btn btn-sm ${hasReturnRequest ? 'btn-disabled' : 'btn-secondary'}`}
                  >
                    {hasReturnRequest ? 'Return Requested' : 'Request Return'}
                  </button>
                );
              }}
            ]}
            keyField="transaction_id"
            emptyMessage={<div className="empty-state"><BookOpen size={48} /><span>No books currently borrowed</span></div>}
          />
        </div>

        <div className="section">
          <h3>My Book Requests</h3>
          <DataTable
            data={requests}
            columns={[
              { key: 'book_title', header: 'Book', render: (value) => <strong>{value}</strong> },
              { key: 'book_author', header: 'Author' },
              { key: 'request_type', header: 'Request Type', render: (value) => (
                <span className={`request-type ${value.toLowerCase()}`}>
                  {value}
                </span>
              )},
              { key: 'request_date', header: 'Date', render: (value) => (
                <div className="date-info">
                  <Calendar size={14} />
                  {formatDate(value)}
                </div>
              )},
              { key: 'status', header: 'Status', render: (value) => (
                <span className={`status-badge status-${value.toLowerCase()}`}>
                  {value}
                </span>
              )},
              { key: 'notes', header: 'Notes', render: (value) => value || '-' }
            ]}
            keyField="request_id"
            emptyMessage={<div className="empty-state"><User size={48} /><span>No requests made</span></div>}
          />
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default MyBooks;