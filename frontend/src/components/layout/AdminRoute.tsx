import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

/**
 * AdminRoute — Bảo vệ route /admin chỉ cho phép role "admin".
 * Nếu chưa đăng nhập: redirect /auth
 * Nếu không phải admin: redirect /search (403 UX)
 */
export const AdminRoute: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) return null;

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  if (user?.role !== 'admin') {
    return <Navigate to="/search" replace />;
  }

  return <Outlet />;
};
