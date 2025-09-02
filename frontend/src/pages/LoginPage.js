import React from 'react';
import { BookOpen, User } from 'lucide-react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import { useAuth } from '../hooks/useAuth';
import { authService } from '../services/authService';
import { loginSchema } from '../utils/validationSchemas';
import { getErrorMessage } from '../utils/errorHandler';
import { ENV_CONFIG } from '../config/environment';
import PasswordInput from '../components/common/PasswordInput';

const LoginPage = () => {
  const { login } = useAuth();

  const handleSubmit = async (values, { setSubmitting, setStatus }) => {
    setStatus('');
    try {
      const userData = await authService.login(values);
      login(userData);
    } catch (err) {
      const errorInfo = getErrorMessage(err);
      setStatus(errorInfo.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDemoLogin = (role, setFieldValue) => {
    if (!ENV_CONFIG.DEMO_CREDENTIALS) return;
    
    const demoCredentials = ENV_CONFIG.DEMO_CREDENTIALS[role];
    if (demoCredentials) {
      setFieldValue('username', demoCredentials.username);
      setFieldValue('password', demoCredentials.password);
    }
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="floating-books">
          <BookOpen className="book-icon book-1" />
          <BookOpen className="book-icon book-2" />
          <BookOpen className="book-icon book-3" />
        </div>
      </div>
      
      <div className="login-card">
        <div className="login-header">
          <div className="logo">
            <BookOpen size={48} className="logo-icon" />
            <h1>Library Management</h1>
          </div>
          <p className="subtitle">Welcome back! Please sign in to continue</p>
        </div>

        <Formik
          initialValues={{ username: '', password: '' }}
          validationSchema={loginSchema}
          onSubmit={handleSubmit}
        >
          {({ isSubmitting, status, setFieldValue }) => (
            <>
              <Form className="login-form">
                <div className="form-group">
                  <label htmlFor="username">Username</label>
                  <div className="input-wrapper">
                    <User className="input-icon" size={20} />
                    <Field
                      id="username"
                      name="username"
                      type="text"
                      placeholder="Enter your username"
                    />
                  </div>
                  <ErrorMessage name="username" component="div" className="field-error" />
                </div>

                <div className="form-group">
                  <label htmlFor="password">Password</label>
                  <Field name="password">
                    {({ field }) => (
                      <PasswordInput
                        {...field}
                        placeholder="Enter your password"
                      />
                    )}
                  </Field>
                  <ErrorMessage name="password" component="div" className="field-error" />
                </div>

                {status && <div className="error-message">{status}</div>}

                <button type="submit" className="login-button" disabled={isSubmitting}>
                  {isSubmitting ? 'Signing in...' : 'Sign In'}
                </button>
              </Form>

              {ENV_CONFIG.IS_DEVELOPMENT && (
                <div className="demo-section">
                  <p className="demo-text">Try demo accounts:</p>
                  <div className="demo-buttons">
                    <button 
                      onClick={() => handleDemoLogin('admin', setFieldValue)} 
                      className="demo-button admin"
                    >
                      Admin Demo
                    </button>
                    <button 
                      onClick={() => handleDemoLogin('user', setFieldValue)} 
                      className="demo-button user"
                    >
                      User Demo
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </Formik>
      </div>
    </div>
  );
};

export default LoginPage;