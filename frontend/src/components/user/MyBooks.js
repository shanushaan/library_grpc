import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useDispatch } from 'react-redux';
import { Calendar, User, BookOpen, Clock, AlertTriangle } from 'lucide-react';
import { showNotification } from '../../store/slices/uiSlice';
import { incrementPendingCount } from '../../store/slices/bookRequestsSlice';
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
      dispatch(showNotification({ message: 'Error fetching your books', type: 'error' }));
    } finally {
      setLoading(false);
    }
  };

  const requestReturn = async (transactionId, bookTitle) => {
    try {
      const response = await axios.post(API_CONFIG.getVersionedUrl('/user/book-request'), {
        book_id: 0, // Will be ignored for return requests
        request_type: 'RETURN',
        user_id: user.user_id,
        transaction_id: transactionId,
        notes: `Return request for ${bookTitle}`
      });
      
      dispatch(showNotification({ message: response.data.message, type: 'success' }));
      dispatch(incrementPendingCount());
      fetchMyBooks(); // Refresh the list
    } catch (error) {
      dispatch(showNotification({ message: error.response?.data?.detail || 'Error requesting return', type: 'error' }));
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
    <div className="page-content my-books">
      <h2>My Books</h2>

      <div className="section">
        <h3>Currently Borrowed Books</h3>
        {borrowedBooks.length === 0 ? (
          <div className="empty-state">
            <BookOpen size={48} />
            <p>No books currently borrowed</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Book</th>
                  <th>Author</th>
                  <th>Borrowed Date</th>
                  <th>Due Date</th>
                  <th>Fine</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {borrowedBooks.map(book => (
                  <tr key={book.transaction_id} className={isOverdue(book.due_date) ? 'overdue-row' : ''}>
                    <td>
                      <div className="book-info">
                        <strong>{book.book_title}</strong>
                        {isOverdue(book.due_date) && <AlertTriangle size={16} className="overdue-icon" />}
                      </div>
                    </td>
                    <td>{book.book_author}</td>
                    <td>
                      <div className="date-info">
                        <Calendar size={14} />
                        {formatDate(book.transaction_date)}
                      </div>
                    </td>
                    <td>
                      <div className={`date-info ${isOverdue(book.due_date) ? 'overdue' : ''}`}>
                        <Clock size={14} />
                        {formatDate(book.due_date)}
                      </div>
                    </td>
                    <td>
                      <span className={`fine-amount ${book.fine_amount > 0 ? 'has-fine' : ''}`}>
                        ${book.fine_amount || 0}
                      </span>
                    </td>
                    <td>
                      <button 
                        onClick={() => requestReturn(book.transaction_id, book.book_title)}
                        className="btn btn-secondary btn-sm"
                      >
                        Request Return
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="section">
        <h3>My Book Requests</h3>
        {requests.length === 0 ? (
          <div className="empty-state">
            <User size={48} />
            <p>No requests made</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Book</th>
                  <th>Author</th>
                  <th>Request Type</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {requests.map(request => (
                  <tr key={request.request_id}>
                    <td><strong>{request.book_title}</strong></td>
                    <td>{request.book_author}</td>
                    <td>
                      <span className={`request-type ${request.request_type.toLowerCase()}`}>
                        {request.request_type}
                      </span>
                    </td>
                    <td>
                      <div className="date-info">
                        <Calendar size={14} />
                        {formatDate(request.request_date)}
                      </div>
                    </td>
                    <td>
                      <span className={`status-badge status-${request.status.toLowerCase()}`}>
                        {request.status}
                      </span>
                    </td>
                    <td>{request.notes || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyBooks;