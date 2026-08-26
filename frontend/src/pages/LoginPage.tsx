/**
 * FILE: src/pages/LoginPage.tsx
 *
 * Gateway page — uses DashboardFactory to resolve the route.
 * Sets AuthContext so every downstream dashboard knows which user is active.
 *
 * MOCK CREDENTIALS map email → real userId from users.json
 * (usr_720465595 = Gabriel Manda; add more users here as needed)
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { DashboardFactory } from '../patterns/DashboardFactory';
import type { UserRole } from '../patterns/DashboardFactory';
import { useAuth } from '../context/AuthContext';
import { Hash, ArrowRight, Eye, EyeOff } from 'lucide-react';

// ─── Mock credential store ────────────────────────────────────────────────────
// Maps login email → real userId from mock server's users.json
interface Creds {
  password:  string;
  role:      UserRole;
  userId:    string;   // must match userId in users.json
  govId:     string;
  fullName:  string;
}

const MOCK_CREDENTIALS: Record<string, Creds> = {
  'official@mospi.gov.in': {
    password: 'official123',
    role:     'official',
    userId:   'usr_720465595',   // Gabriel Manda — Under Secretary
    govId:    'EMP-6282',
    fullName: 'Gabriel Manda',
  },
  'admin@mospi.gov.in': {
    password: 'admin123',
    role:     'admin',
    userId:   'usr_admin_001',
    govId:    'ADMIN-001',
    fullName: 'MoSPI Admin',
  },
  'megha@mospi.gov.in': {
    password: 'official123',
    role:     'official',
    userId:   'usr_200142973',   // Megha Balasubramanian — Deputy Director
    govId:    'EMP-4633',
    fullName: 'Megha Balasubramanian',
  },
};

const LoginPage: React.FC = () => {
  const navigate          = useNavigate();
  const { setUser }       = useAuth();
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    setTimeout(() => {
      const creds = MOCK_CREDENTIALS[email.toLowerCase()];
      if (!creds || creds.password !== password) {
        setError('Invalid email or password. Please try again.');
        setLoading(false);
        return;
      }

      // ── 1. Write to AuthContext so dashboards know who is logged in ────────
      setUser({
        userId:   creds.userId,
        govId:    creds.govId,
        fullName: creds.fullName,
        role:     creds.role,
      });

      // ── 2. Factory resolves the correct dashboard route ────────────────────
      const destinationPath = DashboardFactory.getNavigationPath(creds.role, creds.userId);
      setLoading(false);
      navigate(destinationPath, { replace: true });
    }, 800);
  };

  const fillCredentials = (preset: 'official' | 'admin' | 'megha') => {
    const map = {
      official: { email: 'official@mospi.gov.in', pass: 'official123' },
      admin:    { email: 'admin@mospi.gov.in',    pass: 'admin123' },
      megha:    { email: 'megha@mospi.gov.in',    pass: 'official123' },
    };
    setEmail(map[preset].email);
    setPassword(map[preset].pass);
    setError('');
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-[#f8fafc] dark:bg-slate-900 font-sans transition-colors duration-300">
      {/* Background */}
      <div
        className="absolute inset-0 z-0 pointer-events-none opacity-[0.20] dark:opacity-10 dark:invert"
        style={{
          backgroundImage: `url('/bg-new-topo.png')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          transform: 'scale(1.2) translateX(-5%)',
        }}
      />

      <div className="relative z-10 w-full max-w-md px-4">
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
            <button onClick={() => fillCredentials('official')}
              className="flex-1 py-1.5 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 text-[10px] font-bold rounded-md border border-slate-200 dark:border-slate-600 transition-all">
              Gabriel (Official)
            </button>
            <button onClick={() => fillCredentials('megha')}
              className="flex-1 py-1.5 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 text-[10px] font-bold rounded-md border border-slate-200 dark:border-slate-600 transition-all">
              Megha (Official)
            </button>
            <button onClick={() => fillCredentials('admin')}
              className="flex-1 py-1.5 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 text-[10px] font-bold rounded-md border border-slate-200 dark:border-slate-600 transition-all">
              Admin
            </button>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            {/* Email */}
            <div>
              <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                placeholder="official@mospi.gov.in"
                className="w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 text-[13px] text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-[#2b4c7e]/30 focus:border-[#2b4c7e] transition-all"
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPass ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 text-[13px] text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-[#2b4c7e]/30 focus:border-[#2b4c7e] transition-all pr-10"
                />
                <button type="button" onClick={() => setShowPass(v => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200" tabIndex={-1}>
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
            Role-based routing powered by DashboardFactory pattern
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
