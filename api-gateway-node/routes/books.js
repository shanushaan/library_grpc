const express = require('express');
const { grpcCall } = require('../utils/grpcClient');
const HTTP_STATUS = require('../constants/httpStatus');

const router = express.Router();

// User book search
router.get('/user/books/search', async (req, res) => {
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
    res.status(HTTP_STATUS.OK).json(books);
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

// Admin book management
router.get('/admin/books', async (req, res) => {
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
    res.status(HTTP_STATUS.OK).json(books);
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

router.post('/admin/books', async (req, res) => {
  try {
    const response = await grpcCall('CreateBook', {
      title: req.body.title,
      author: req.body.author,
      genre: req.body.genre,
      published_year: req.body.published_year,
      available_copies: req.body.available_copies
    });
    
    if (response.success) {
      res.status(HTTP_STATUS.CREATED).json({
        book_id: response.book.book_id,
        message: response.message
      });
    } else {
      res.status(HTTP_STATUS.BAD_REQUEST).json({ error: response.message });
    }
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

router.put('/admin/books/:book_id', async (req, res) => {
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
      res.status(HTTP_STATUS.OK).json({ message: response.message });
    } else {
      res.status(HTTP_STATUS.BAD_REQUEST).json({ error: response.message });
    }
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

router.delete('/admin/books/:book_id', async (req, res) => {
  try {
    const response = await grpcCall('DeleteBook', {
      book_id: parseInt(req.params.book_id)
    });
    
    if (response.success) {
      res.status(HTTP_STATUS.OK).json({ message: response.message });
    } else {
      res.status(HTTP_STATUS.BAD_REQUEST).json({ error: response.message });
    }
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

module.exports = router;