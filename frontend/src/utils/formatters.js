export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleDateString();
};

export const isOverdue = (dueDateString) => {
  if (!dueDateString) return false;
  return new Date(dueDateString) < new Date();
};

export const getStatusColor = (status) => {
  switch (status) {
    case 'BORROWED': return 'borrowed';
    case 'RETURNED': return 'returned';
    case 'OVERDUE': return 'overdue';
    case 'PENDING': return 'pending';
    case 'APPROVED': return 'approved';
    case 'REJECTED': return 'rejected';
    default: return 'unknown';
  }
};