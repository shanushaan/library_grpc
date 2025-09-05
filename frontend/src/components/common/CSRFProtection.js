import { useEffect } from 'react';
import { csrfService } from '../../services/csrfService';

export const CSRFProtection = ({ children }) => {
  useEffect(() => {
    csrfService.fetchToken();
  }, []);

  return children;
};

export const withCSRFProtection = (WrappedComponent) => {
  return (props) => (
    <CSRFProtection>
      <WrappedComponent {...props} />
    </CSRFProtection>
  );
};