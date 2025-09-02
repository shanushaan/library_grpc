import React from 'react';

const LoadingScreen = ({ message = "Loading Library Management System..." }) => {
  return (
    <div className="loading-screen">
      <div className="loading-spinner"></div>
      <p>{message}</p>
    </div>
  );
};

export default LoadingScreen;