const express = require('express');
const { grpcCall } = require('../utils/grpcClient');
const HTTP_STATUS = require('../constants/httpStatus');

const router = express.Router();

router.post('/login', async (req, res) => {
  try {
    const response = await grpcCall('AuthenticateUser', {
      username: req.body.username,
      password: req.body.password
    });
    
    if (response.success) {
      res.status(HTTP_STATUS.OK).json({
        user_id: response.user.user_id,
        username: response.user.username,
        email: response.user.email,
        role: response.user.role,
        message: response.message
      });
    } else {
      res.status(HTTP_STATUS.UNAUTHORIZED).json({ error: response.message });
    }
  } catch (error) {
    res.status(HTTP_STATUS.INTERNAL_SERVER_ERROR).json({ error: 'Service unavailable' });
  }
});

module.exports = router;