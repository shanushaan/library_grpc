const express = require('express');
const { grpcCall } = require('../utils/grpcClient');
const { sendNotification } = require('../websocket');
const HTTP_STATUS = require('../constants/httpStatus');

const router = express.Router();

router.post('/user/book-request', async (req, res) => {
  try {
    const response = await grpcCall('CreateUserBookRequest', {
      user_id: req.body.user_id,
      book_id: req.body.book_id,
      request_type: req.body.request_type,
      transaction_id: req.body.transaction_id || 0,
      notes: req.body.notes || ''
    });
    
    if (response.success) {
      res.status(HTTP_STATUS.CREATED).json({
        request_id: response.request.request_id,
        message: response.message,
        status: response.request.status
      });
    } else {
      res.status(HTTP_STATUS.BAD_REQUEST).json({ error: response.message });
    }
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

router.get('/user/:user_id/book-requests', async (req, res) => {
  try {
    const userId = parseInt(req.params.user_id);
    const [requestsResponse, booksResponse, transactionsResponse] = await Promise.all([
      grpcCall('GetBookRequests', { status: '' }),
      grpcCall('GetBooks', { search_query: '' }),
      grpcCall('GetTransactions', { user_id: userId, status: '' })
    ]);
    
    const booksDict = {};
    booksResponse.books.forEach(book => {
      booksDict[book.book_id] = book;
    });
    
    const transactionsDict = {};
    transactionsResponse.transactions.forEach(txn => {
      transactionsDict[txn.transaction_id] = txn;
    });
    
    const userRequests = requestsResponse.requests
      .filter(req => req.user_id === userId)
      .map(req => {
        let book_title = 'Unknown';
        let book_author = 'Unknown';
        
        if (req.request_type === 'RETURN' && req.transaction_id && req.transaction_id > 0) {
          const transaction = transactionsDict[req.transaction_id];
          if (transaction) {
            const book = booksDict[transaction.book_id];
            if (book) {
              book_title = book.title;
              book_author = book.author;
            }
          }
        } else if (req.book_id > 0) {
          const book = booksDict[req.book_id];
          if (book) {
            book_title = book.title;
            book_author = book.author;
          }
        }
        return {
          request_id: req.request_id,
          user_id: req.user_id,
          book_id: req.book_id,
          book_title,
          book_author,
          request_type: req.request_type,
          status: req.status,
          request_date: req.request_date,
          notes: req.notes,
        };
      });
    
    res.status(HTTP_STATUS.OK).json(userRequests);
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

router.get('/admin/book-requests', async (req, res) => {
  try {
    const [requestsResponse, booksResponse, usersResponse, transactionsResponse] = await Promise.all([
      grpcCall('GetBookRequests', { status: 'PENDING' }),
      grpcCall('GetBooks', { search_query: '' }),
      grpcCall('GetUsers', {}),
      grpcCall('GetTransactions', { user_id: 0, status: '' })
    ]);
    
    const booksDict = {};
    booksResponse.books.forEach(book => {
      booksDict[book.book_id] = book;
    });
    
    const usersDict = {};
    usersResponse.users.forEach(user => {
      usersDict[user.user_id] = user.username;
    });
    
    const transactionsDict = {};
    transactionsResponse.transactions.forEach(txn => {
      transactionsDict[txn.transaction_id] = txn;
    });
    
    const requests = requestsResponse.requests.map(req => {
      let book_title = 'Unknown';
      let book_author = 'Unknown';
      let available_copies = 0;
      
      if (req.request_type === 'RETURN' && req.transaction_id) {
        const transaction = transactionsDict[req.transaction_id];
        if (transaction) {
          const book = booksDict[transaction.book_id];
          if (book) {
            book_title = book.title;
            book_author = book.author;
            available_copies = book.available_copies;
          }
        }
      } else if (req.book_id > 0) {
        const book = booksDict[req.book_id];
        if (book) {
          book_title = book.title;
          book_author = book.author;
          available_copies = book.available_copies;
        }
      }
      
      return {
        request_id: req.request_id,
        user_id: req.user_id,
        user_name: usersDict[req.user_id] || `User ${req.user_id}`,
        book_id: req.book_id,
        book_title,
        book_author,
        available_copies,
        request_type: req.request_type,
        status: req.status,
        request_date: req.request_date,
        notes: req.notes
      };
    });
    
    res.status(HTTP_STATUS.OK).json(requests);
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

router.post('/admin/book-requests/:request_id/approve', async (req, res) => {
  try {
    const requestId = parseInt(req.params.request_id);
    const response = await grpcCall('ApproveBookRequest', {
      request_id: requestId,
      admin_id: 1
    });
    
    if (response.success) {
      const request = await grpcCall('GetBookRequests', { status: '' });
      const approvedRequest = request.requests.find(r => r.request_id === requestId);
      if (approvedRequest) {
        sendNotification(approvedRequest.user_id, {
          type: 'REQUEST_APPROVED',
          message: `Your ${approvedRequest.request_type.toLowerCase()} request has been approved`,
          requestId: requestId
        });
      }
      res.status(HTTP_STATUS.OK).json({ message: response.message });
    } else {
      res.status(HTTP_STATUS.BAD_REQUEST).json({ error: response.message });
    }
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

router.post('/admin/book-requests/:request_id/reject', async (req, res) => {
  try {
    const requestId = parseInt(req.params.request_id);
    const response = await grpcCall('RejectBookRequest', {
      request_id: requestId,
      admin_id: 1,
      notes: req.body.notes || ''
    });
    
    if (response.success) {
      const request = await grpcCall('GetBookRequests', { status: '' });
      const rejectedRequest = request.requests.find(r => r.request_id === requestId);
      if (rejectedRequest) {
        sendNotification(rejectedRequest.user_id, {
          type: 'REQUEST_REJECTED',
          message: `Your ${rejectedRequest.request_type.toLowerCase()} request has been rejected`,
          requestId: requestId
        });
      }
      res.status(HTTP_STATUS.OK).json({ message: response.message });
    } else {
      res.status(HTTP_STATUS.BAD_REQUEST).json({ error: response.message });
    }
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

module.exports = router;