const express = require('express');
const { grpcCall } = require('../utils/grpcClient');
const HTTP_STATUS = require('../constants/httpStatus');

const router = express.Router();

router.get('/admin/stats', async (req, res) => {
  try {
    const response = await grpcCall('GetTransactions', { user_id: 0, status: '' });
    const borrowedCount = response.transactions.filter(txn => txn.status === 'BORROWED').length;
    const overdueCount = response.transactions.filter(txn => 
      txn.status === 'BORROWED' && txn.due_date < new Date().toISOString()
    ).length;
    
    res.status(HTTP_STATUS.OK).json({
      borrowed_books: borrowedCount,
      overdue_books: overdueCount
    });
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

module.exports = router;