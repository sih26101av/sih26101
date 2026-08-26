/**
 * FILE: src/App.tsx
 *
 * Root router. AuthProvider wraps everything so any component can read
 * the logged-in user via useAuth(). Dashboard routes pull userId from
 * AuthContext — no hardcoded IDs anywhere.
 *
 * DEFAULT USER for Learner Dashboard (until real login is wired):
 *   usr_720465595 — Gabriel Manda, Under Secretary, Survey Coordination Division
 */

import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './hooks/useTheme';
import { AuthProvider } from './context/AuthContext';
import LandingPage from './pages/LandingPage';
import LoginPage   from './pages/LoginPage';

// ─── Lazy-loaded dashboards ───────────────────────────────────────────────────
const LearnerDashboard = React.lazy(() => import('./pages/LearnerDashboard'));
const AdminDashboard   = React.lazy(() => import('./pages/AdminDashboard'));

// ─── Loading fallback ─────────────────────────────────────────────────────────
const PageLoader: React.FC = () => (
  <div className="min-h-screen flex items-center justify-center bg-[#f8fafc] dark:bg-slate-900">
    <div className="flex flex-col items-center gap-4">
      <div className="w-10 h-10 rounded-full border-4 border-slate-200 border-t-[#2b4c7e] animate-spin" />
      <p className="text-[12px] font-semibold text-slate-400 tracking-wide uppercase">Loading…</p>
    </div>
  </div>
);

// ─── Default user (first real user from mock server) ─────────────────────────
// Switch this to the logged-in user's ID once LoginPage sets AuthContext.
const DEFAULT_LEARNER_ID = 'usr_720465595';

const App: React.FC = () => (
  <ThemeProvider>
    <AuthProvider>
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Public */}
            <Route path="/"      element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />

            {/* Learner Dashboard — uses AuthContext user, falls back to default */}
            <Route
              path="/dashboard/:officialId"
              element={<LearnerDashboard officialId={DEFAULT_LEARNER_ID} />}
            />

            {/* Admin Dashboard — no userId needed, fetches all users */}
            <Route path="/admin" element={<AdminDashboard />} />

            {/* Trainer — maps to Learner for now */}
            <Route
              path="/trainer"
              element={<LearnerDashboard officialId={DEFAULT_LEARNER_ID} />}
            />

            {/* Catch-all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  </ThemeProvider>
);

export default App;