const express = require('express');
const { grpcCall } = require('../utils/grpcClient');
const HTTP_STATUS = require('../constants/httpStatus');

const router = express.Router();

router.get('/admin/users', async (req, res) => {
  try {
    const response = await grpcCall('GetUsers', {});
    const users = response.users.map(user => ({
      user_id: user.user_id,
      username: user.username,
      email: user.email,
      role: user.role,
      is_active: user.is_active
    }));
    res.status(HTTP_STATUS.OK).json(users);
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

router.post('/admin/users', async (req, res) => {
  try {
    const response = await grpcCall('CreateUser', {
      username: req.body.username,
      email: req.body.email,
      password: req.body.password,
      role: req.body.role
    });
    
    if (response.success) {
      res.status(HTTP_STATUS.CREATED).json({
        user_id: response.user.user_id,
        message: response.message
      });
    } else {
      res.status(HTTP_STATUS.BAD_REQUEST).json({ error: response.message });
    }
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

router.put('/admin/users/:user_id', async (req, res) => {
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
      res.status(HTTP_STATUS.OK).json({ message: response.message });
    } else {
      res.status(HTTP_STATUS.BAD_REQUEST).json({ error: response.message });
    }
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

router.get('/user/:user_id/stats', async (req, res) => {
  try {
    const response = await grpcCall('GetUserStats', {
      user_id: parseInt(req.params.user_id)
    });
    
    res.status(HTTP_STATUS.OK).json({
      total_books_taken: response.total_books_taken,
      currently_borrowed: response.currently_borrowed,
      overdue_books: response.overdue_books,
      total_fine: response.total_fine
    });
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

module.exports = router;