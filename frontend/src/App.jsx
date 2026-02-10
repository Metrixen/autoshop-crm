import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/auth/Login';
import CustomerDashboard from './pages/customer/Dashboard';
import StaffDashboard from './pages/staff/Dashboard';
import Vehicles from './pages/staff/Vehicles';
import VehicleDetail from './pages/staff/VehicleDetail';
import Customers from './pages/staff/Customers';
import WorkOrders from './pages/staff/WorkOrders';
import Invoices from './pages/staff/Invoices';
import './i18n/i18n';

// Protected Route Component
const ProtectedRoute = ({ children, requireStaff = false, requireCustomer = false }) => {
  const { isAuthenticated, isStaff, isCustomer, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requireStaff && !isStaff) {
    return <Navigate to="/customer" replace />;
  }

  if (requireCustomer && !isCustomer) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// Public Route Component
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isStaff, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to={isStaff ? "/dashboard" : "/customer"} replace />;
  }

  return children;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            }
          />

          {/* Customer Routes */}
          <Route
            path="/customer"
            element={
              <ProtectedRoute requireCustomer>
                <CustomerDashboard />
              </ProtectedRoute>
            }
          />

          {/* Staff Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute requireStaff>
                <StaffDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/vehicles"
            element={
              <ProtectedRoute requireStaff>
                <Vehicles />
              </ProtectedRoute>
            }
          />
          <Route
            path="/vehicles/:id"
            element={
              <ProtectedRoute requireStaff>
                <VehicleDetail />
              </ProtectedRoute>
            }
          />
          <Route
            path="/customers"
            element={
              <ProtectedRoute requireStaff>
                <Customers />
              </ProtectedRoute>
            }
          />
          <Route
            path="/work-orders"
            element={
              <ProtectedRoute requireStaff>
                <WorkOrders />
              </ProtectedRoute>
            }
          />
          <Route
            path="/invoices"
            element={
              <ProtectedRoute requireStaff>
                <Invoices />
              </ProtectedRoute>
            }
          />
          <Route
            path="/appointments"
            element={
              <ProtectedRoute requireStaff>
                <StaffDashboard />
              </ProtectedRoute>
            }
          />

          {/* Default Route */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          
          {/* 404 Route */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
