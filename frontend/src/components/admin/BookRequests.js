import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../../styles/BookRequests.css';

const BookRequests = ({ user }) => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8001/admin/book-requests');
      setRequests(response.data);
    } catch (error) {
      setMessage('Error fetching requests');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (requestId) => {
    try {
      const response = await axios.post(`http://localhost:8001/admin/book-requests/${requestId}/approve`);
      setMessage(response.data.message);
      fetchRequests(); // Refresh the list
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Error approving request');
    }
  };

  const handleReject = async (requestId) => {
    const notes = prompt('Reason for rejection (optional):');
    try {
      const response = await axios.post(`http://localhost:8001/admin/book-requests/${requestId}/reject?notes=${encodeURIComponent(notes || '')}`);
      setMessage(response.data.message);
      fetchRequests(); // Refresh the list
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Error rejecting request');
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="book-requests">
      <h2>Pending Book Requests</h2>
      
      {message && <div className="message">{message}</div>}

      {requests.length === 0 ? (
        <p>No pending requests</p>
      ) : (
        <div className="requests-table">
          <table>
            <thead>
              <tr>
                <th>User</th>
                <th>Book</th>
                <th>Author</th>
                <th>Type</th>
                <th>Date</th>
                <th>Available</th>
                <th>Notes</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {requests.map(request => (
                <tr key={request.request_id}>
                  <td>{request.user_name}</td>
                  <td>{request.book_title}</td>
                  <td>{request.book_author}</td>
                  <td>
                    <span className={`badge ${request.request_type.toLowerCase()}`}>
                      {request.request_type}
                    </span>
                  </td>
                  <td>{request.request_date}</td>
                  <td>
                    {request.request_type === 'ISSUE' ? (
                      <span className={request.available_copies > 0 ? 'available' : 'unavailable'}>
                        {request.available_copies} copies
                      </span>
                    ) : (
                      'N/A'
                    )}
                  </td>
                  <td>{request.notes || '-'}</td>
                  <td>
                    <div className="actions">
                      <button 
                        onClick={() => handleApprove(request.request_id)}
                        className="btn-approve"
                        disabled={request.request_type === 'ISSUE' && request.available_copies <= 0}
                      >
                        Approve
                      </button>
                      <button 
                        onClick={() => handleReject(request.request_id)}
                        className="btn-reject"
                      >
                        Reject
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default BookRequests;