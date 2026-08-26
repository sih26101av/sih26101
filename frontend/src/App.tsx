/**
 * FILE: src/App.tsx
 *
 * The router only knows about route paths. The DashboardFactory is the single
 * source of truth for which component mounts at each path.
 */

import React, { Suspense } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "./hooks/useTheme";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";

// ─── Factory-resolved lazy components ─────────────────────────────────────────
// App.tsx does NOT import LearnerDashboard/AdminDashboard directly.
// The factory handles lazy loading internally.
const LearnerDashboard = React.lazy(() => import("./pages/LearnerDashboard"));
const AdminDashboard   = React.lazy(() => import("./pages/AdminDashboard"));

// ─── Loading fallback (reused for all lazy routes) ────────────────────────────
const PageLoader: React.FC = () => (
  <div className="min-h-screen flex items-center justify-center bg-[#f8fafc]">
    <div className="flex flex-col items-center gap-4">
      <div className="w-10 h-10 rounded-full border-4 border-slate-200 border-t-[#2b4c7e] animate-spin" />
      <p className="text-[12px] font-semibold text-slate-400 tracking-wide uppercase">Loading Dashboard…</p>
    </div>
  </div>
);

// EMP-8472 matches the live FastAPI backend user ID (kept here for reference)
const ACTIVE_OFFICIAL_ID = "EMP-8472";

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* ── Public Routes ─────────────────────────────────────────── */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />

            {/* ── Factory-resolved Dashboard Routes ─────────────────────── */}
            {/* Paths are dictated by DashboardFactory route registrations:
                  official → /dashboard/:officialId
                  admin    → /admin
                  trainer  → /trainer (fallback to LearnerDashboard for now) */}
            <Route
              path="/dashboard/:officialId"
              element={<LearnerDashboard officialId={ACTIVE_OFFICIAL_ID} />}
            />
            <Route
              path="/admin"
              element={<AdminDashboard />}
            />
            <Route
              path="/trainer"
              element={<LearnerDashboard officialId={ACTIVE_OFFICIAL_ID} />}
            />

            {/* ── Catch-all ─────────────────────────────────────────────── */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;