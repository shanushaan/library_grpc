export const getErrorMessage = (error) => {
  // Network errors
  if (!error.response) {
    if (error.code === 'NETWORK_ERROR' || error.message === 'Network Error') {
      return {
        message: 'Unable to connect to server. Please check your internet connection.',
        type: 'network'
      };
    }
    return {
      message: 'Connection failed. Please try again.',
      type: 'network'
    };
  }

  const { status, data } = error.response;

  // Authentication errors
  if (status === 401) {
    return {
      message: data?.error || 'Invalid username or password',
      type: 'auth'
    };
  }

  // Validation errors
  if (status === 400) {
    return {
      message: data?.error || 'Invalid request. Please check your input.',
      type: 'validation'
    };
  }

  // Permission errors
  if (status === 403) {
    return {
      message: 'You do not have permission to perform this action.',
      type: 'permission'
    };
  }

  // Not found errors
  if (status === 404) {
    return {
      message: 'The requested resource was not found.',
      type: 'notfound'
    };
  }

  // Server errors
  if (status >= 500) {
    return {
      message: 'Server error. Please try again later or contact support.',
      type: 'server'
    };
  }

  // Default error
  return {
    message: data?.error || 'An unexpected error occurred. Please try again.',
    type: 'unknown'
  };
};

export const handleApiError = (error, dispatch, showNotification) => {
  const errorInfo = getErrorMessage(error);
  dispatch(showNotification({ 
    message: errorInfo.message, 
    type: 'error',
    errorType: errorInfo.type
  }));
  return errorInfo;
};