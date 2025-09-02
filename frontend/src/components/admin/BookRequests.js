import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchBookRequests, approveBookRequest, rejectBookRequest } from '../../store/slices/bookRequestsSlice';
import { openRejectModal, closeRejectModal, showNotification } from '../../store/slices/uiSlice';
import RejectModal from '../common/RejectModal';
import DataTable from '../common/DataTable';
import ErrorBoundary from '../common/ErrorBoundary';
import '../../styles/BookRequests.css';

const BookRequests = ({ user }) => {
  const dispatch = useDispatch();
  const { data: requests, loading } = useSelector(state => state.bookRequests);
  const { rejectModal } = useSelector(state => state.ui.modals);

  const handleApprove = async (requestId) => {
    try {
      const result = await dispatch(approveBookRequest(requestId)).unwrap();
      dispatch(showNotification({ message: result.message, type: 'success' }));
    } catch (error) {
      dispatch(showNotification({ message: 'Error approving request', type: 'error' }));
    }
  };

  const handleReject = (requestId) => {
    dispatch(openRejectModal(requestId));
  };

  const confirmReject = async (notes) => {
    const requestId = rejectModal.requestId;
    
    try {
      const result = await dispatch(rejectBookRequest({ requestId, notes })).unwrap();
      dispatch(showNotification({ message: result.message, type: 'success' }));
      dispatch(closeRejectModal());
    } catch (error) {
      dispatch(showNotification({ message: 'Error rejecting request', type: 'error' }));
    }
  };

  useEffect(() => {
    dispatch(fetchBookRequests());
  }, [dispatch]);

  const columns = [
    { key: 'user_name', header: 'User' },
    { key: 'book_title', header: 'Book' },
    { key: 'book_author', header: 'Author' },
    { 
      key: 'request_type', 
      header: 'Type',
      render: (value) => (
        <span className={`badge ${value.toLowerCase()}`}>
          {value}
        </span>
      )
    },
    { key: 'request_date', header: 'Date' },
    { 
      key: 'available_copies', 
      header: 'Available',
      render: (value, row) => (
        row.request_type === 'ISSUE' ? (
          <span className={value > 0 ? 'available' : 'unavailable'}>
            {value} copies
          </span>
        ) : 'N/A'
      )
    },
    { key: 'notes', header: 'Notes', render: (value) => value || '-' },
    {
      key: 'actions',
      header: 'Actions',
      render: (_, row) => (
        <div className="actions">
          <button 
            onClick={() => handleApprove(row.request_id)}
            className="btn-approve"
            disabled={row.request_type === 'ISSUE' && row.available_copies <= 0}
          >
            Approve
          </button>
          <button 
            onClick={() => handleReject(row.request_id)}
            className="btn-reject"
          >
            Reject
          </button>
        </div>
      )
    }
  ];

  if (loading) return <div>Loading...</div>;

  return (
    <ErrorBoundary fallbackMessage="Book requests management unavailable.">
      <div className="book-requests">
        <h2>Pending Book Requests</h2>
        
        <DataTable
          data={requests}
          columns={columns}
          keyField="request_id"
          emptyMessage="No pending requests"
          className="requests-table"
        />
        
        <RejectModal
          isOpen={rejectModal.isOpen}
          onClose={() => dispatch(closeRejectModal())}
          onConfirm={confirmReject}
          title="Reject Book Request"
        />
      </div>
    </ErrorBoundary>
  );
};

export default BookRequests;