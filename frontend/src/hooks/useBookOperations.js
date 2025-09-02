import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { showNotification } from '../store/slices/uiSlice';
import { incrementPendingCount } from '../store/slices/bookRequestsSlice';
import { API_CONFIG } from '../config/api';

export const useBookOperations = (user) => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);

  const requestBook = async (bookId) => {
    setLoading(true);
    try {
      const response = await fetch(API_CONFIG.getVersionedUrl('/user/book-request'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          book_id: bookId,
          request_type: 'ISSUE',
          user_id: user.user_id,
          notes: 'Book request from catalog'
        })
      });
      
      if (response.ok) {
        dispatch(showNotification({ message: 'Book request submitted successfully!', type: 'success' }));
        dispatch(incrementPendingCount());
      } else {
        dispatch(showNotification({ message: 'Failed to submit book request', type: 'error' }));
      }
    } catch (error) {
      dispatch(showNotification({ message: 'Error submitting request', type: 'error' }));
    } finally {
      setLoading(false);
    }
  };

  const requestReturn = async (transactionId, bookTitle) => {
    setLoading(true);
    try {
      const response = await fetch(API_CONFIG.getVersionedUrl('/user/book-request'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          book_id: 0,
          request_type: 'RETURN',
          user_id: user.user_id,
          transaction_id: transactionId,
          notes: `Return request for ${bookTitle}`
        })
      });
      
      const data = await response.json();
      dispatch(showNotification({ message: data.message, type: 'success' }));
      dispatch(incrementPendingCount());
    } catch (error) {
      dispatch(showNotification({ message: 'Error requesting return', type: 'error' }));
    } finally {
      setLoading(false);
    }
  };

  return { requestBook, requestReturn, loading };
};