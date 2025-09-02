const express = require('express');
const cors = require('cors');
const http = require('http');
const { initWebSocket } = require('./websocket');
const HTTP_STATUS = require('./constants/httpStatus');

// Import route modules
const authRoutes = require('./routes/auth');
const bookRoutes = require('./routes/books');
const userRoutes = require('./routes/users');
const transactionRoutes = require('./routes/transactions');
const requestRoutes = require('./routes/requests');
const statsRoutes = require('./routes/stats');

const app = express();
const PORT = process.env.PORT || 8001;

// Middleware
app.use(cors());
app.use(express.json());

// API versioning
const API_V1 = '/api/v1';

// Routes
app.use(API_V1, authRoutes);
app.use(API_V1, bookRoutes);
app.use(API_V1, userRoutes);
app.use(API_V1, transactionRoutes);
app.use(API_V1, requestRoutes);
app.use(API_V1, statsRoutes);

// Root endpoint
app.get('/', (req, res) => {
  res.status(HTTP_STATUS.OK).json({ 
    message: 'Library API Gateway - Node.js Version', 
    grpc_backend: `${process.env.GRPC_SERVER_HOST || 'localhost'}:${process.env.GRPC_SERVER_PORT || '50051'}` 
  });
});

const server = http.createServer(app);
initWebSocket(server);

server.listen(PORT, () => {
  console.log(`Node.js API Gateway running on port ${PORT}`);
});