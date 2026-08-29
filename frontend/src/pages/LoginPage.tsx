/**
 * FILE: src/pages/LoginPage.tsx
 *
 * Gateway page — calls My App Backend /auth/login (real JWT auth).
 * Uses DashboardFactory to resolve the post-login route.
 *
 * Credentials: username = usr_XXXXXXXXX (iGOT userId) or "admin"
 * Default passwords: lowercase(firstName) + last 2 digits of userId
 * e.g. Gabriel / usr_720465595 → gabriel95
 */

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Hash, ArrowRight, Eye, EyeOff, ArrowLeft } from 'lucide-react';

interface LoginPageProps {
  isModal?: boolean;
  onClose?: () => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ isModal = false, onClose }) => {
  const navigate         = useNavigate();
  const location         = useLocation();
  const { login }        = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);

  // Where to go after login if redirected from a protected route
  const from = (location.state as any)?.from?.pathname ?? null;

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // login() calls /auth/login on port 8000 and updates AuthContext
      await login(username.trim(), password);

      // AuthContext now holds the user + mustChangePassword flag.
      // ChangePasswordPage or ProtectedRoute will handle the force-redirect;
      // we just need to navigate to the intended destination or dashboard.
      // Re-read the updated context is tricky synchronously, so we rely on
      // ProtectedRoute to redirect to /change-password if needed.
      // For normal flow, use the 'from' state or DashboardFactory.
      //
      // We call getMe in AuthContext.login, so 'role' is available after await.
      // Access the user from context via a small re-read trick:
      //   We navigate speculatively; ProtectedRoute will intercept if needed.
      if (from && from !== '/login' && from !== '/change-password') {
        navigate(from, { replace: true });
      } else {
        // Let ProtectedRoute figure out where to send based on role.
        // Navigate to a neutral protected route; it will redirect correctly.
        navigate('/dashboard-redirect', { replace: true });
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Login failed. Please check your credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Quick-fill helpers for the demo (SIH presentation convenience)
  const fillCredentials = (preset: 'gabriel' | 'admin' | 'priya') => {
    const map = {
      gabriel: { username: 'usr_720465595', pass: 'gabriel95' },
      admin:   { username: 'admin',         pass: 'admin123'  },
      priya:   { username: 'usr_EMP8472',   pass: 'priya72'   },
    };
    setUsername(map[preset].username);
    setPassword(map[preset].pass);
    setError('');
  };

  return (
    <div className={isModal ? "fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm font-sans transition-colors duration-300" : "min-h-screen flex items-center justify-center relative overflow-hidden bg-[#f8fafc] dark:bg-slate-900 font-sans transition-colors duration-300"}>
      {/* Background */}
      {!isModal && (
        <div
          className="absolute inset-0 z-0 pointer-events-none opacity-[0.20] dark:opacity-10 dark:invert"
          style={{
            backgroundImage: `url('/bg-new-topo.png')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            transform: 'scale(1.2) translateX(-5%)',
          }}
        />
      )}

      <div className="relative z-10 w-full max-w-md px-4">
        {isModal && (
          <button 
            onClick={onClose}
            className="absolute -top-12 left-4 flex items-center gap-2 text-white/90 hover:text-white bg-slate-800/50 hover:bg-slate-800 px-3 py-1.5 rounded-full text-[12px] font-bold backdrop-blur-md transition-all shadow-md"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Home
          </button>
        )}
        
        {/* Logo */}
        <div className="flex flex-col items-center mb-8 cursor-default">
          <div className="flex items-center gap-1.5">
            <div className="flex flex-col gap-[3px] justify-center mt-0.5">
              <div className="w-1.5 h-1.5 rounded-full bg-[#0f172a] dark:bg-white" />
              <div className="w-1.5 h-1.5 rounded-full bg-[#16A34A]" />
            </div>
            <span className="font-bold text-[22px] text-[#0f172a] dark:text-white tracking-tight leading-none">MoSPI</span>
          </div>
          <span className="text-[8px] text-slate-400 font-semibold tracking-wide uppercase mt-1">
            Skill Intelligence Platform
          </span>
        </div>

        {/* Card */}
        <div className="bg-white/90 dark:bg-slate-800/90 backdrop-blur-md rounded-2xl shadow-xl shadow-slate-200/60 dark:shadow-none border border-slate-200/80 dark:border-slate-700/60 p-8 transition-colors duration-300">
          <h2 className="text-[20px] font-bold text-[#0f172a] dark:text-white mb-1">Welcome back</h2>
          <p className="text-[13px] text-slate-500 dark:text-slate-400 mb-6">Sign in to access your MoSPI dashboard.</p>

          {/* Quick-fill buttons */}
          <div className="flex gap-2 mb-6">
            <button
              onClick={() => fillCredentials('gabriel')}
              className="flex-1 py-1.5 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 text-[10px] font-bold rounded-md border border-slate-200 dark:border-slate-600 transition-all"
            >
              Gabriel (Official)
            </button>
            <button
              onClick={() => fillCredentials('priya')}
              className="flex-1 py-1.5 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 text-[10px] font-bold rounded-md border border-slate-200 dark:border-slate-600 transition-all"
            >
              Priya (Official)
            </button>
            <button
              onClick={() => fillCredentials('admin')}
              className="flex-1 py-1.5 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 text-[10px] font-bold rounded-md border border-slate-200 dark:border-slate-600 transition-all"
            >
              Admin
            </button>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            {/* Username */}
            <div>
              <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-1.5">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
                placeholder="usr_720465595 or admin"
                className="w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 text-[13px] text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-[#2b4c7e]/30 focus:border-[#2b4c7e] transition-all"
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPass ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 text-[13px] text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-[#2b4c7e]/30 focus:border-[#2b4c7e] transition-all pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(v => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                  tabIndex={-1}
                >
                  {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <p className="text-[12px] text-red-500 font-medium bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800/50 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-b from-[#2b4c7e] to-[#0d1b2a] text-white text-[13px] font-bold rounded-lg shadow-[0_8px_20px_-6px_rgba(13,27,42,0.7)] hover:from-[#3a5d91] hover:to-[#162a42] transition-all disabled:opacity-60 disabled:cursor-not-allowed"
              style={{ textShadow: '0 1px 2px rgba(0,0,0,0.6)' }}
            >
              {loading ? (
                <svg className="animate-spin w-4 h-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
              ) : (
                <>Sign In <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </form>

          <div className="mt-4 flex items-center gap-1.5 text-[11px] text-slate-400">
            <Hash className="w-3 h-3" />
            JWT auth via MoSPI LMS Backend · Role-based routing via DashboardFactory
          </div>
        </div>

        <p className="text-center mt-6 text-[11px] text-slate-400">
          © {new Date().getFullYear()} Ministry of Statistics and Programme Implementation
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
