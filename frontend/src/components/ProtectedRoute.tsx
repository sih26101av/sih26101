/**
 * FILE: src/components/ProtectedRoute.tsx
 *
 * PATTERN: Wrapper / Guard Component
 * ─────────────────────────────────────────────────────────────────────────────
 * Enforces authentication and role-based access control at the router level.
 *
 * Behaviour matrix
 * ─────────────────
 * isLoading              → renders a spinner (silent-refresh in progress)
 * !user                  → <Navigate to="/login" />
 * user.mustChangePassword→ <Navigate to="/change-password" /> (unless already there)
 * requiredRole && wrong  → <Navigate to="/" />   (insufficient permissions)
 * all checks pass        → renders {children}
 * ─────────────────────────────────────────────────────────────────────────────
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { UserRole } from '../patterns/DashboardFactory';

interface ProtectedRouteProps {
  children: React.ReactNode;
  /** If provided, the user's role must match this value. */
  requiredRole?: UserRole;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRole }) => {
  const { user, mustChangePassword, isLoading } = useAuth();
  const location = useLocation();

  // ── While silent-refresh is running, show a minimal spinner ─────────────────
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f8fafc] dark:bg-slate-900">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 rounded-full border-4 border-slate-200 border-t-[#2b4c7e] animate-spin" />
          <p className="text-[12px] font-semibold text-slate-400 tracking-wide uppercase">
            Verifying session…
          </p>
        </div>
      </div>
    );
  }

  // ── Not authenticated → go to login, preserve intended destination ───────────
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // ── Must change password → force to change-password page ─────────────────────
  if (mustChangePassword && location.pathname !== '/change-password') {
    return <Navigate to="/change-password" replace />;
  }

  // ── Role check ───────────────────────────────────────────────────────────────
  if (requiredRole && user.role !== requiredRole) {
    // Learner trying to reach /admin → bounce to landing
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
