/**
 * FILE: src/pages/ChangePasswordPage.tsx
 *
 * Forced on first login (must_change_password=True) and accessible any time
 * from either dashboard's user menu.
 *
 * After a successful change:
 * - Calls authApi.changePassword with the current access token.
 * - Clears mustChangePassword in AuthContext.
 * - Navigates to the correct dashboard based on the user's role.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, EyeOff, KeyRound, ShieldCheck, ArrowRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { changePassword } from '../services/authApi';
import { DashboardFactory } from '../patterns/DashboardFactory';

const ChangePasswordPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, accessToken, mustChangePassword, setMustChangePassword } = useAuth();

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword]         = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrent, setShowCurrent]         = useState(false);
  const [showNew, setShowNew]                 = useState(false);
  const [showConfirm, setShowConfirm]         = useState(false);
  const [error, setError]                     = useState('');
  const [loading, setLoading]                 = useState(false);
  const [success, setSuccess]                 = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match.');
      return;
    }
    if (newPassword.length < 6) {
      setError('New password must be at least 6 characters.');
      return;
    }

    if (!accessToken) {
      setError('Session expired. Please log in again.');
      navigate('/login', { replace: true });
      return;
    }

    setLoading(true);
    try {
      await changePassword(accessToken, currentPassword, newPassword);
      setMustChangePassword(false);
      setSuccess(true);

      // Brief success flash, then redirect
      setTimeout(() => {
        if (!user) { navigate('/login', { replace: true }); return; }
        const dest = DashboardFactory.getNavigationPath(user.role, user.username);
        navigate(dest, { replace: true });
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to change password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#f8fafc] dark:bg-slate-900 font-sans transition-colors duration-300">
      {/* Subtle background */}
      <div
        className="absolute inset-0 z-0 pointer-events-none opacity-[0.15] dark:opacity-10 dark:invert"
        style={{
          backgroundImage: `url('/bg-new-topo.png')`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      />

      <div className="relative z-10 w-full max-w-md px-4">
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="flex items-center gap-1.5">
            <div className="flex flex-col gap-[3px] justify-center mt-0.5">
              <div className="w-1.5 h-1.5 rounded-full bg-[#0f172a] dark:bg-white" />
              <div className="w-1.5 h-1.5 rounded-full bg-[#16A34A]" />
            </div>
            <span className="font-bold text-[22px] text-[#0f172a] dark:text-white tracking-tight leading-none">
              MoSPI
            </span>
          </div>
          <span className="text-[8px] text-slate-400 font-semibold tracking-wide uppercase mt-1">
            Skill Intelligence Platform
          </span>
        </div>

        {/* Card */}
        <div className="bg-white/90 dark:bg-slate-800/90 backdrop-blur-md rounded-2xl shadow-xl border border-slate-200/80 dark:border-slate-700/60 p-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-9 h-9 rounded-xl bg-[#2b4c7e]/10 flex items-center justify-center">
              <KeyRound className="w-5 h-5 text-[#2b4c7e]" />
            </div>
            <div>
              <h2 className="text-[18px] font-bold text-[#0f172a] dark:text-white leading-tight">
                {mustChangePassword ? 'Set Your Password' : 'Change Password'}
              </h2>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                {mustChangePassword
                  ? 'First login detected — please set a new secure password.'
                  : 'Update your account password.'}
              </p>
            </div>
          </div>

          {/* Success state */}
          {success ? (
            <div className="mt-6 flex flex-col items-center gap-3 py-6">
              <div className="w-14 h-14 rounded-full bg-green-50 border border-green-100 flex items-center justify-center">
                <ShieldCheck className="w-7 h-7 text-green-500" />
              </div>
              <p className="text-[14px] font-semibold text-slate-700 dark:text-slate-200">
                Password updated successfully!
              </p>
              <p className="text-[12px] text-slate-400">Redirecting to your dashboard…</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              {/* Current password */}
              <div>
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-1.5">
                  Current Password
                </label>
                <div className="relative">
                  <input
                    type={showCurrent ? 'text' : 'password'}
                    value={currentPassword}
                    onChange={e => setCurrentPassword(e.target.value)}
                    required
                    placeholder="••••••••"
                    className="w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 text-[13px] text-slate-800 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#2b4c7e]/30 focus:border-[#2b4c7e] transition-all pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowCurrent(v => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700"
                    tabIndex={-1}
                  >
                    {showCurrent ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* New password */}
              <div>
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-1.5">
                  New Password
                </label>
                <div className="relative">
                  <input
                    type={showNew ? 'text' : 'password'}
                    value={newPassword}
                    onChange={e => setNewPassword(e.target.value)}
                    required
                    minLength={6}
                    placeholder="Min. 6 characters"
                    className="w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 text-[13px] text-slate-800 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#2b4c7e]/30 focus:border-[#2b4c7e] transition-all pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowNew(v => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700"
                    tabIndex={-1}
                  >
                    {showNew ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Confirm new password */}
              <div>
                <label className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-1.5">
                  Confirm New Password
                </label>
                <div className="relative">
                  <input
                    type={showConfirm ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={e => setConfirmPassword(e.target.value)}
                    required
                    placeholder="••••••••"
                    className="w-full px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-700 text-[13px] text-slate-800 dark:text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-[#2b4c7e]/30 focus:border-[#2b4c7e] transition-all pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirm(v => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700"
                    tabIndex={-1}
                  >
                    {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
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
                  <>Update Password <ArrowRight className="w-4 h-4" /></>
                )}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChangePasswordPage;
