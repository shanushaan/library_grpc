const express = require('express');
const { grpcCall } = require('../utils/grpcClient');
const HTTP_STATUS = require('../constants/httpStatus');

const router = express.Router();

router.post('/admin/issue-book', async (req, res) => {
  try {
    const response = await grpcCall('IssueBook', {
      book_id: req.body.book_id,
      member_id: req.body.user_id,
      admin_id: 1
    });
    
    if (response.success) {
      res.status(HTTP_STATUS.CREATED).json({
        transaction_id: response.transaction.transaction_id,
        message: response.message
      });
    } else {
      res.status(HTTP_STATUS.BAD_REQUEST).json({ error: response.message });
    }
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

router.post('/admin/return-book', async (req, res) => {
  try {
    const response = await grpcCall('ReturnBook', {
      transaction_id: req.body.transaction_id,
      admin_id: 1
    });
    
    if (response.success) {
      res.status(HTTP_STATUS.OK).json({
        transaction_id: response.transaction.transaction_id,
        fine_amount: response.transaction.fine_amount,
        message: response.message
      });
    } else {
      res.status(HTTP_STATUS.BAD_REQUEST).json({ error: response.message });
    }
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

router.get('/admin/transactions', async (req, res) => {
  try {
    const [transactionsResponse, usersResponse, booksResponse] = await Promise.all([
      grpcCall('GetTransactions', {
        user_id: req.query.user_id || 0,
        status: req.query.status || ''
      }),
      grpcCall('GetUsers', {}),
      grpcCall('GetBooks', { search_query: '' })
    ]);
    
    const usersDict = {};
    usersResponse.users.forEach(user => {
      usersDict[user.user_id] = user.username;
    });
    
    const booksDict = {};
    booksResponse.books.forEach(book => {
      booksDict[book.book_id] = book.title;
    });
    
    const transactions = transactionsResponse.transactions.map(txn => ({
      transaction_id: txn.transaction_id,
      user_id: txn.member_id,
      username: usersDict[txn.member_id] || `User ${txn.member_id}`,
      book_id: txn.book_id,
      book_title: booksDict[txn.book_id] || 'Unknown Book',
      transaction_type: txn.transaction_type,
      transaction_date: txn.transaction_date,
      due_date: txn.due_date,
      return_date: txn.return_date,
      status: txn.status,
      fine_amount: txn.fine_amount
    }));
    
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 20;
    const startIdx = (page - 1) * limit;
    const endIdx = startIdx + limit;
    const paginatedTransactions = transactions.slice(startIdx, endIdx);
    
    res.status(HTTP_STATUS.OK).json({
      transactions: paginatedTransactions,
      total_count: transactions.length,
      page,
      limit,
      total_pages: Math.ceil(transactions.length / limit)
    });
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

router.get('/user/:user_id/transactions', async (req, res) => {
  try {
    const userId = parseInt(req.params.user_id);
    const status = req.query.status || '';
    
    const response = await grpcCall('GetUserTransactions', {
      user_id: userId,
      status: status
    });
    
    const transactions = response.transactions.map(txn => ({
      transaction_id: txn.transaction_id,
      book_id: txn.book_id,
      book_title: txn.book_title,
      book_author: txn.book_author,
      transaction_type: txn.transaction_type,
      transaction_date: txn.transaction_date,
      due_date: txn.due_date,
      return_date: txn.return_date,
      status: txn.status,
      fine_amount: txn.fine_amount
    }));
    
    res.status(HTTP_STATUS.OK).json(transactions);
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

module.exports = router;