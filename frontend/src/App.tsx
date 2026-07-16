import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import MechanicDashboard from './pages/mechanic/Dashboard';
import AdminDashboard from './pages/admin/Dashboard';
import ShowroomDashboard from './pages/showroom/Dashboard';
import OwnerDashboard from './pages/owner/Dashboard';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Dashboard router that redirects based on role
const DashboardRouter: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Route to appropriate dashboard based on role
  switch (user.role) {
    case 'admin':
      return <Navigate to="/admin/dashboard" replace />;
    case 'showroom':
      return <Navigate to="/showroom/dashboard" replace />;
    case 'mechanic':
      return <Navigate to="/mechanic/dashboard" replace />;
    case 'owner':
      return <Navigate to="/owner/dashboard" replace />;
    default:
      return <Navigate to="/login" replace />;
  }
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AuthProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            
            {/* Dashboard router */}
            <Route path="/dashboard" element={<DashboardRouter />} />
            
            {/* Protected role-specific routes */}
            <Route
              path="/admin/dashboard"
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/showroom/dashboard"
              element={
                <ProtectedRoute allowedRoles={['showroom']}>
                  <ShowroomDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/mechanic/dashboard"
              element={
                <ProtectedRoute allowedRoles={['mechanic']}>
                  <MechanicDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/owner/dashboard"
              element={
                <ProtectedRoute allowedRoles={['owner']}>
                  <OwnerDashboard />
                </ProtectedRoute>
              }
            />
            
            {/* Default redirect */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* 404 fallback */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </AuthProvider>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
