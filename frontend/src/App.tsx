/**
 * FILE: src/App.tsx
 *
 * Root router.
 *
 * Auth flow:
 *  - AuthProvider manages JWT access token (in state) + refresh cookie (httpOnly).
 *  - On mount it silently attempts /auth/refresh to restore session.
 *  - ProtectedRoute guards all private routes — redirects to /login if not
 *    authenticated, /change-password if must_change_password=true.
 *
 * Route                Role guard      Notes
 * ─────────────────── ─────────────── ──────────────────────────────────
 * /                   none            Landing page (public)
 * /login              none            Login page (public)
 * /policy/:slug       none            Statutory GIGW pages (terms, privacy,
 *                                     copyright, hyperlinking, disclaimer,
 *                                     accessibility, screen reader, help,
 *                                     feedback, sitemap) — content/policies.tsx
 * /not-found, *       none            GIGW-compliant 404 page
 * /change-password    authenticated   Forced first-login + accessible anytime
 * /dashboard/:id      authenticated   Learner / Official role
 * /admin              authenticated   admin role only
 * /trainer            authenticated   Learner-equivalent for now
 * /dashboard-redirect authenticated   Role-aware post-login redirect helper
 */

import React, { Suspense, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { ThemeProvider } from './hooks/useTheme';
import { AccessibilityProvider } from './context/AccessibilityContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { setApiToken, registerLogoutCallback } from './services/api';
import { DashboardFactory } from './patterns/DashboardFactory';
import LandingPage from './pages/LandingPage';
import LoginPage   from './pages/LoginPage';
import ChangePasswordPage from './pages/ChangePasswordPage';
import ProtectedRoute from './components/ProtectedRoute';
import PolicyPage from './pages/PolicyPage';
import NotFoundPage from './pages/NotFoundPage';

// ─── Lazy-loaded dashboards ────────────────────────────────────────────────────
const LearnerDashboard = React.lazy(() => import('./pages/LearnerDashboard'));
const AdminDashboard   = React.lazy(() => import('./pages/AdminDashboard'));
const AssessmentPage   = React.lazy(() => import('./pages/AssessmentPage'));

// ─── Loading fallback ──────────────────────────────────────────────────────────
const PageLoader: React.FC = () => (
  <div className="min-h-screen flex items-center justify-center bg-[#f8fafc] dark:bg-slate-900">
    <div className="flex flex-col items-center gap-4">
      <div className="w-10 h-10 rounded-full border-4 border-slate-200 border-t-[#2b4c7e] animate-spin" />
      <p className="text-[12px] font-semibold text-slate-400 tracking-wide uppercase">Loading…</p>
    </div>
  </div>
);

// ─── Token bridge: syncs AuthContext → api.ts module-level store ──────────────
// This component sits inside AuthProvider so it can read the context.
const TokenBridge: React.FC = () => {
  const { accessToken, logout } = useAuth();

  useEffect(() => {
    // Push token into the api module whenever it changes
    setApiToken(accessToken);
  }, [accessToken]);

  useEffect(() => {
    // Register logout so the 401-interceptor in api.ts can call it
    registerLogoutCallback(() => {
      logout();
    });
  }, [logout]);

  return null;
};

// ─── Post-login role-aware redirect ───────────────────────────────────────────
// /dashboard-redirect is a tiny protected route that reads the user's role
// from AuthContext and delegates to DashboardFactory.
const DashboardRedirect: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      const dest = DashboardFactory.getNavigationPath(user.role, user.username);
      navigate(dest, { replace: true });
    }
  }, [user, navigate]);

  return <PageLoader />;
};

// ─── App ───────────────────────────────────────────────────────────────────────
const App: React.FC = () => (
  <ThemeProvider>
    <AccessibilityProvider>
      <AuthProvider>
      <BrowserRouter>
        <TokenBridge />
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* ── Public ──────────────────────────────────────────────────── */}
            <Route path="/"      element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />

            {/* ── Statutory pages required on every GoI site ──────────────── */}
            <Route path="/policy/:slug" element={<PolicyPage />} />
            <Route path="/sitemap" element={<Navigate to="/policy/sitemap" replace />} />
            <Route path="/accessibility" element={<Navigate to="/policy/accessibility-statement" replace />} />

            {/* ── Post-login role redirect ────────────────────────────────── */}
            <Route
              path="/dashboard-redirect"
              element={
                <ProtectedRoute>
                  <DashboardRedirect />
                </ProtectedRoute>
              }
            />

            {/* ── Change password (authenticated, any role) ───────────────── */}
            <Route
              path="/change-password"
              element={
                <ProtectedRoute>
                  <ChangePasswordPage />
                </ProtectedRoute>
              }
            />

            {/* ── Learner Dashboard ────────────────────────────────────────── */}
            <Route
              path="/dashboard/:officialId"
              element={
                <ProtectedRoute requiredRole="official">
                  <LearnerDashboard />
                </ProtectedRoute>
              }
            />

            {/* ── Admin Dashboard ──────────────────────────────────────────── */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute requiredRole="admin">
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />

            {/* ── Trainer (maps to Learner for now) ───────────────────────── */}
            <Route
              path="/trainer"
              element={
                <ProtectedRoute>
                  <LearnerDashboard />
                </ProtectedRoute>
              }
            />

            {/* ── Assessment Page ────────────────────────────────────────────── */}
            <Route
              path="/assessment"
              element={
                <ProtectedRoute>
                  <AssessmentPage />
                </ProtectedRoute>
              }
            />

            {/* ── Catch-all: a helpful error page, not a silent redirect ──── */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
      </AuthProvider>
    </AccessibilityProvider>
  </ThemeProvider>
);

export default App;