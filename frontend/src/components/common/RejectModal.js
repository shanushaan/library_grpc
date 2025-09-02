import React, { useState } from 'react';
import { X } from 'lucide-react';
import '../../styles/Modal.css';

const RejectModal = ({ isOpen, onClose, onConfirm, title = "Reject Request" }) => {
  const [notes, setNotes] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onConfirm(notes);
    setNotes('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3>{title}</h3>
          <button onClick={onClose} className="modal-close">
            <X size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <label htmlFor="rejection-notes">Reason for rejection (optional):</label>
            <textarea
              id="rejection-notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Enter reason for rejection..."
              rows={4}
            />
          </div>
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-danger">
              Reject
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RejectModal;