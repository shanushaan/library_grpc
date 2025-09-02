import { 
  LayoutDashboard, 
  BookOpen, 
  Users, 
  Receipt, 
  BarChart3,
  Settings,
  FileText,
  Search,
  History,
  User
} from 'lucide-react';

import DashboardOverview from '../components/admin/DashboardOverview';
import BooksManagement from '../components/admin/BooksManagement';
import BookRequests from '../components/admin/BookRequests';
import UsersManagement from '../components/admin/UsersManagement';
import TransactionsManagement from '../components/admin/TransactionsManagement';
import ReportsAnalytics from '../components/admin/ReportsAnalytics';

import UserOverview from '../components/user/UserOverview';
import BookCatalog from '../components/user/BookCatalog';
import MyBooks from '../components/user/MyBooks';
import BookHistory from '../components/user/BookHistory';
import UserProfile from '../components/user/UserProfile';

export const adminRoutes = [
  { 
    id: 'overview', 
    label: 'Librarian Dashboard', 
    icon: LayoutDashboard, 
    path: '/admin',
    component: DashboardOverview 
  },
  { 
    id: 'books', 
    label: 'Librarian Books', 
    icon: BookOpen, 
    path: '/admin/books',
    component: BooksManagement 
  },
  { 
    id: 'requests', 
    label: 'Book Requests', 
    icon: FileText, 
    path: '/admin/requests',
    component: BookRequests 
  },
  { 
    id: 'users', 
    label: 'Library Users', 
    icon: Users, 
    path: '/admin/users',
    component: UsersManagement 
  },
  { 
    id: 'transactions', 
    label: 'Transactions', 
    icon: Receipt, 
    path: '/admin/transactions',
    component: TransactionsManagement 
  },
  { 
    id: 'reports', 
    label: 'Reports & Analytics', 
    icon: BarChart3, 
    path: '/admin/reports',
    component: ReportsAnalytics 
  },
  { 
    id: 'settings', 
    label: 'Settings', 
    icon: Settings, 
    path: '/admin/settings',
    component: () => <div className="page-content">Settings Page</div>
  }
];

export const userRoutes = [
  { 
    id: 'overview', 
    label: 'Dashboard', 
    icon: LayoutDashboard, 
    path: '/dashboard',
    component: UserOverview
  },
  { 
    id: 'catalog', 
    label: 'Browse Books', 
    icon: Search, 
    path: '/dashboard/catalog',
    component: BookCatalog
  },
  { 
    id: 'my-books', 
    label: 'My Books', 
    icon: BookOpen, 
    path: '/dashboard/my-books',
    component: MyBooks
  },
  { 
    id: 'history', 
    label: 'Reading History', 
    icon: History, 
    path: '/dashboard/history',
    component: BookHistory 
  },
  { 
    id: 'profile', 
    label: 'My Profile', 
    icon: User, 
    path: '/dashboard/profile',
    component: UserProfile 
  }
];