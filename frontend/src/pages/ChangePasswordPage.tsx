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
import { AshokaChakra, GovEmblem } from '../components/gov/GovUI';
import GovUtilityBar from '../components/gov/GovUtilityBar';
import GovFooter from '../components/gov/GovFooter';
import { usePageTitle } from '../hooks/usePageTitle';

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

  usePageTitle('Change Password', 'Set a new password for your KarmaSkill account.');

  return (
    <div className="flex min-h-screen flex-col">
      <a href="#main-content" className="skip-link">Skip to main content</a>
      <GovUtilityBar mainId="main-content" />
      <div className="tricolor-strip" />
      <main id="main-content" tabIndex={-1} className="flex flex-1 items-center justify-center relative overflow-hidden gov-page-bg font-sans transition-colors duration-300 py-10">
      {/* Government header band */}
      <div className="absolute inset-x-0 top-0 h-[42vh] bg-gradient-to-br from-gov-ink via-gov-navy to-gov-blue" />
      <div className="absolute inset-x-0 top-[42vh] tricolor-strip" />
      <div className="absolute -right-32 -top-32 text-white/[0.06] pointer-events-none">
        <AshokaChakra size={560} strokeWidth={0.8} className="animate-spin-slow" />
      </div>

      <div className="relative z-10 w-full max-w-md px-4 animate-scale-in">
        {/* Logo */}
        <div className="flex items-center justify-center gap-3 mb-6 text-white">
          <GovEmblem size={48} />
          <div className="leading-tight">
            <div className="text-[11px] font-semibold text-gov-saffron" lang="hi">सांख्यिकी और कार्यक्रम कार्यान्वयन मंत्रालय</div>
            <div className="font-serif font-bold text-[15px]">Ministry of Statistics &amp; PI</div>
            <div className="text-[9.5px] font-bold uppercase tracking-[0.2em] text-white/60">Skill Intelligence Platform</div>
          </div>
        </div>

        {/* Card */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-gov-lg border border-gov-line dark:border-slate-700/60 overflow-hidden">
          <div className="tricolor-strip" />
          <div className="p-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-gov-navy flex items-center justify-center shadow-gov">
              <KeyRound className="w-5 h-5 text-gov-saffron" />
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
                <label htmlFor="cp-current" className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-1.5">
                  Current Password
                </label>
                <div className="relative">
                  <input
                    id="cp-current"
                    name="cp-current"
                    type={showCurrent ? 'text' : 'password'}
                    autoComplete="current-password"
                    aria-invalid={!!error}
                    aria-describedby={error ? 'cp-error' : undefined}
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
                    aria-pressed={showCurrent}
                    aria-label={showCurrent ? 'Hide the current password' : 'Show the current password'}
                  >
                    {showCurrent ? <EyeOff className="w-4 h-4" aria-hidden="true" /> : <Eye className="w-4 h-4" aria-hidden="true" />}
                  </button>
                </div>
              </div>

              {/* New password */}
              <div>
                <label htmlFor="cp-new" className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-1.5">
                  New Password
                </label>
                <div className="relative">
                  <input
                    id="cp-new"
                    name="cp-new"
                    type={showNew ? 'text' : 'password'}
                    autoComplete="new-password"
                    aria-invalid={!!error}
                    aria-describedby={error ? 'cp-error' : undefined}
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
                    aria-pressed={showNew}
                    aria-label={showNew ? 'Hide the new password' : 'Show the new password'}
                  >
                    {showNew ? <EyeOff className="w-4 h-4" aria-hidden="true" /> : <Eye className="w-4 h-4" aria-hidden="true" />}
                  </button>
                </div>
              </div>

              {/* Confirm new password */}
              <div>
                <label htmlFor="cp-confirm" className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-1.5">
                  Confirm New Password
                </label>
                <div className="relative">
                  <input
                    id="cp-confirm"
                    name="cp-confirm"
                    type={showConfirm ? 'text' : 'password'}
                    autoComplete="new-password"
                    aria-invalid={!!error}
                    aria-describedby={error ? 'cp-error' : undefined}
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
                    aria-pressed={showConfirm}
                    aria-label={showConfirm ? 'Hide the confirmation' : 'Show the confirmation'}
                  >
                    {showConfirm ? <EyeOff className="w-4 h-4" aria-hidden="true" /> : <Eye className="w-4 h-4" aria-hidden="true" />}
                  </button>
                </div>
              </div>

              {/* Error */}
              {error && (
                <p id="cp-error" role="alert" className="text-[12px] text-red-500 font-medium bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-800/50 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="gov-btn-primary w-full mt-2 !py-3"
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
      </main>
      <GovFooter variant="compact" />
    </div>
  );
};

export default ChangePasswordPage;
