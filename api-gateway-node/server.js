const express = require('express');
const cors = require('cors');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8001;

// Middleware
app.use(cors());
app.use(express.json());

// Load protobuf
const PROTO_PATH = path.join(__dirname, 'proto/library_service.proto');
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

const libraryProto = grpc.loadPackageDefinition(packageDefinition).library;

// gRPC client
const grpcHost = process.env.GRPC_SERVER_HOST || 'localhost';
const grpcPort = process.env.GRPC_SERVER_PORT || '50051';
const client = new libraryProto.LibraryService(`${grpcHost}:${grpcPort}`, grpc.credentials.createInsecure());

// Helper function to promisify gRPC calls
const grpcCall = (method, request) => {
  return new Promise((resolve, reject) => {
    client[method](request, (error, response) => {
      if (error) reject(error);
      else resolve(response);
    });
  });
};

// API versioning
const API_V1 = '/api/v1';

// Routes
app.post(`${API_V1}/login`, async (req, res) => {
  try {
    const response = await grpcCall('AuthenticateUser', {
      username: req.body.username,
      password: req.body.password
    });
    
    if (response.success) {
      res.json({
        user_id: response.user.user_id,
        username: response.user.username,
        email: response.user.email,
        role: response.user.role,
        message: response.message
      });
    } else {
      res.status(401).json({ error: response.message });
    }
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.get(`${API_V1}/user/books/search`, async (req, res) => {
  try {
    const response = await grpcCall('GetBooks', { search_query: req.query.q || '' });
    const books = response.books.map(book => ({
      book_id: book.book_id,
      title: book.title,
      author: book.author,
      genre: book.genre,
      published_year: book.published_year,
      available_copies: book.available_copies,
      can_request: book.available_copies > 0
    }));
    res.json(books);
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.post(`${API_V1}/user/book-request`, async (req, res) => {
  try {
    const response = await grpcCall('CreateUserBookRequest', {
      user_id: req.body.user_id,
      book_id: req.body.book_id,
      request_type: req.body.request_type,
      transaction_id: req.body.transaction_id || 0,
      notes: req.body.notes || ''
    });
    
    if (response.success) {
      res.json({
        request_id: response.request.request_id,
        message: response.message,
        status: response.request.status
      });
    } else {
      res.status(400).json({ error: response.message });
    }
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.get(`${API_V1}/admin/books`, async (req, res) => {
  try {
    const response = await grpcCall('GetBooks', { search_query: req.query.q || '' });
    const books = response.books.map(book => ({
      book_id: book.book_id,
      title: book.title,
      author: book.author,
      genre: book.genre,
      published_year: book.published_year,
      available_copies: book.available_copies
    }));
    res.json(books);
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.get(`${API_V1}/admin/users`, async (req, res) => {
  try {
    const response = await grpcCall('GetUsers', {});
    const users = response.users.map(user => ({
      user_id: user.user_id,
      username: user.username,
      email: user.email,
      role: user.role,
      is_active: user.is_active
    }));
    res.json(users);
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.post(`${API_V1}/admin/issue-book`, async (req, res) => {
  try {
    const response = await grpcCall('IssueBook', {
      book_id: req.body.book_id,
      member_id: req.body.user_id,
      admin_id: 1
    });
    
    if (response.success) {
      res.json({
        transaction_id: response.transaction.transaction_id,
        message: response.message
      });
    } else {
      res.status(400).json({ error: response.message });
    }
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.post(`${API_V1}/admin/return-book`, async (req, res) => {
  try {
    const response = await grpcCall('ReturnBook', {
      transaction_id: req.body.transaction_id,
      admin_id: 1
    });
    
    if (response.success) {
      res.json({
        transaction_id: response.transaction.transaction_id,
        fine_amount: response.transaction.fine_amount,
        message: response.message
      });
    } else {
      res.status(400).json({ error: response.message });
    }
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.get(`${API_V1}/admin/transactions`, async (req, res) => {
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
    
    res.json({
      transactions: paginatedTransactions,
      total_count: transactions.length,
      page,
      limit,
      total_pages: Math.ceil(transactions.length / limit)
    });
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.post(`${API_V1}/admin/books`, async (req, res) => {
  try {
    const response = await grpcCall('CreateBook', {
      title: req.body.title,
      author: req.body.author,
      genre: req.body.genre,
      published_year: req.body.published_year,
      available_copies: req.body.available_copies
    });
    
    if (response.success) {
      res.json({
        book_id: response.book.book_id,
        message: response.message
      });
    } else {
      res.status(400).json({ error: response.message });
    }
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.put(`${API_V1}/admin/books/:book_id`, async (req, res) => {
  try {
    const response = await grpcCall('UpdateBook', {
      book_id: parseInt(req.params.book_id),
      title: req.body.title,
      author: req.body.author,
      genre: req.body.genre,
      published_year: req.body.published_year,
      available_copies: req.body.available_copies
    });
    
    if (response.success) {
      res.json({ message: response.message });
    } else {
      res.status(400).json({ error: response.message });
    }
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.delete(`${API_V1}/admin/books/:book_id`, async (req, res) => {
  try {
    const response = await grpcCall('DeleteBook', {
      book_id: parseInt(req.params.book_id)
    });
    
    if (response.success) {
      res.json({ message: response.message });
    } else {
      res.status(400).json({ error: response.message });
    }
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.post(`${API_V1}/admin/users`, async (req, res) => {
  try {
    const response = await grpcCall('CreateUser', {
      username: req.body.username,
      email: req.body.email,
      password: req.body.password,
      role: req.body.role
    });
    
    if (response.success) {
      res.json({
        user_id: response.user.user_id,
        message: response.message
      });
    } else {
      res.status(400).json({ error: response.message });
    }
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.put(`${API_V1}/admin/users/:user_id`, async (req, res) => {
  try {
    const response = await grpcCall('UpdateUser', {
      user_id: parseInt(req.params.user_id),
      username: req.body.username,
      email: req.body.email,
      role: req.body.role,
      is_active: req.body.is_active,
      password: req.body.password || ''
    });
    
    if (response.success) {
      res.json({ message: response.message });
    } else {
      res.status(400).json({ error: response.message });
    }
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.get(`${API_V1}/user/:user_id/stats`, async (req, res) => {
  try {
    const response = await grpcCall('GetUserStats', {
      user_id: parseInt(req.params.user_id)
    });
    
    res.json({
      total_books_taken: response.total_books_taken,
      currently_borrowed: response.currently_borrowed,
      overdue_books: response.overdue_books,
      total_fine: response.total_fine
    });
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.get(`${API_V1}/user/:user_id/transactions`, async (req, res) => {
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
    
    res.json(transactions);
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.get(`${API_V1}/user/:user_id/book-requests`, async (req, res) => {
  try {
    const userId = parseInt(req.params.user_id);
    const [requestsResponse, booksResponse] = await Promise.all([
      grpcCall('GetBookRequests', { status: '' }),
      grpcCall('GetBooks', { search_query: '' })
    ]);
    
    const booksDict = {};
    booksResponse.books.forEach(book => {
      booksDict[book.book_id] = book;
    });
    
    const userRequests = requestsResponse.requests
      .filter(req => req.user_id === userId)
      .map(req => {
        const book = booksDict[req.book_id];
        return {
          request_id: req.request_id,
          user_id: req.user_id,
          book_id: req.book_id,
          book_title: book ? book.title : 'Unknown',
          book_author: book ? book.author : 'Unknown',
          request_type: req.request_type,
          status: req.status,
          request_date: req.request_date,
          notes: req.notes
        };
      });
    
    res.json(userRequests);
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.get(`${API_V1}/admin/book-requests`, async (req, res) => {
  try {
    const [requestsResponse, booksResponse, usersResponse] = await Promise.all([
      grpcCall('GetBookRequests', { status: 'PENDING' }),
      grpcCall('GetBooks', { search_query: '' }),
      grpcCall('GetUsers', {})
    ]);
    
    const booksDict = {};
    booksResponse.books.forEach(book => {
      booksDict[book.book_id] = book;
    });
    
    const usersDict = {};
    usersResponse.users.forEach(user => {
      usersDict[user.user_id] = user.username;
    });
    
    const requests = requestsResponse.requests.map(req => {
      const book = booksDict[req.book_id];
      return {
        request_id: req.request_id,
        user_id: req.user_id,
        user_name: usersDict[req.user_id] || `User ${req.user_id}`,
        book_id: req.book_id,
        book_title: book ? book.title : 'Unknown',
        book_author: book ? book.author : 'Unknown',
        available_copies: book ? book.available_copies : 0,
        request_type: req.request_type,
        status: req.status,
        request_date: req.request_date,
        notes: req.notes
      };
    });
    
    res.json(requests);
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.post(`${API_V1}/admin/book-requests/:request_id/approve`, async (req, res) => {
  try {
    const requestId = parseInt(req.params.request_id);
    const response = await grpcCall('ApproveBookRequest', {
      request_id: requestId,
      admin_id: 1
    });
    
    if (response.success) {
      res.json({ message: response.message });
    } else {
      res.status(400).json({ error: response.message });
    }
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.post(`${API_V1}/admin/book-requests/:request_id/reject`, async (req, res) => {
  try {
    const requestId = parseInt(req.params.request_id);
    const response = await grpcCall('RejectBookRequest', {
      request_id: requestId,
      admin_id: 1,
      notes: req.body.notes || ''
    });
    
    if (response.success) {
      res.json({ message: response.message });
    } else {
      res.status(400).json({ error: response.message });
    }
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.get(`${API_V1}/admin/stats`, async (req, res) => {
  try {
    const response = await grpcCall('GetTransactions', { user_id: 0, status: '' });
    const borrowedCount = response.transactions.filter(txn => txn.status === 'BORROWED').length;
    const overdueCount = response.transactions.filter(txn => 
      txn.status === 'BORROWED' && txn.due_date < new Date().toISOString()
    ).length;
    
    res.json({
      borrowed_books: borrowedCount,
      overdue_books: overdueCount
    });
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.get('/', (req, res) => {
  res.json({ 
    message: 'Library API Gateway - Node.js Version', 
    grpc_backend: `${grpcHost}:${grpcPort}` 
  });
});

app.listen(PORT, () => {
  console.log(`Node.js API Gateway running on port ${PORT}`);
});