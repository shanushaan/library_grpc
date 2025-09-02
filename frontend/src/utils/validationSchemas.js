import * as Yup from 'yup';

export const loginSchema = Yup.object({
  username: Yup.string()
    .min(3, 'Username must be at least 3 characters')
    .max(20, 'Username must be less than 20 characters')
    .required('Username is required'),
  password: Yup.string()
    .min(6, 'Password must be at least 6 characters')
    .required('Password is required')
});

export const bookSchema = Yup.object({
  title: Yup.string()
    .min(2, 'Title must be at least 2 characters')
    .max(100, 'Title must be less than 100 characters')
    .required('Title is required'),
  author: Yup.string()
    .min(2, 'Author must be at least 2 characters')
    .max(50, 'Author must be less than 50 characters')
    .required('Author is required'),
  genre: Yup.string()
    .min(2, 'Genre must be at least 2 characters')
    .max(30, 'Genre must be less than 30 characters')
    .required('Genre is required'),
  published_year: Yup.number()
    .min(1000, 'Year must be valid')
    .max(new Date().getFullYear(), 'Year cannot be in the future')
    .required('Published year is required'),
  available_copies: Yup.number()
    .min(0, 'Copies cannot be negative')
    .max(1000, 'Copies cannot exceed 1000')
    .required('Available copies is required')
});

export const userSchema = Yup.object({
  username: Yup.string()
    .min(3, 'Username must be at least 3 characters')
    .max(20, 'Username must be less than 20 characters')
    .matches(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores')
    .required('Username is required'),
  email: Yup.string()
    .email('Invalid email format')
    .required('Email is required'),
  password: Yup.string()
    .min(6, 'Password must be at least 6 characters')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, 'Password must contain at least one uppercase letter, one lowercase letter, and one number')
    .required('Password is required'),
  role: Yup.string()
    .oneOf(['USER', 'ADMIN'], 'Role must be either USER or ADMIN')
    .required('Role is required')
});

export const bookRequestSchema = Yup.object({
  book_id: Yup.number()
    .positive('Please select a valid book')
    .required('Book selection is required'),
  request_type: Yup.string()
    .oneOf(['ISSUE', 'RETURN'], 'Invalid request type')
    .required('Request type is required'),
  notes: Yup.string()
    .max(200, 'Notes must be less than 200 characters')
});

export const transactionValidation = {
  validateBookAvailability: (book, requestType) => {
    if (requestType === 'ISSUE' && book.available_copies <= 0) {
      return 'This book is currently not available';
    }
    return null;
  },
  
  validateDuplicateIssue: (userTransactions, bookId) => {
    const hasActiveIssue = userTransactions.some(txn => 
      txn.book_id === bookId && txn.status === 'BORROWED'
    );
    if (hasActiveIssue) {
      return 'You already have this book issued';
    }
    return null;
  },
  
  validateUserLimit: (userTransactions, maxBooks = 5) => {
    const activeBorrows = userTransactions.filter(txn => txn.status === 'BORROWED').length;
    if (activeBorrows >= maxBooks) {
      return `You have reached the maximum limit of ${maxBooks} books`;
    }
    return null;
  },
  
  validateReturnEligibility: (userTransactions, bookId) => {
    const hasActiveBorrow = userTransactions.some(txn => 
      txn.book_id === bookId && txn.status === 'BORROWED'
    );
    if (!hasActiveBorrow) {
      return 'You do not have this book issued';
    }
    return null;
  }
};