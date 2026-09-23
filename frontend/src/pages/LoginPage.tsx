/**
 * FILE: src/pages/LoginPage.tsx
 *
 * Gateway page — calls MoSPI LMS Backend /auth/login (real JWT auth).
 * Uses DashboardFactory to resolve the post-login route.
 *
 * Two shapes: `isModal` renders only the card, over the landing page, which
 * already carries the portal chrome. As its own route at /login it wraps the
 * card in the GIGW chrome — skip link, utility strip, <main> landmark and the
 * statutory footer — so a user who lands here directly gets the same portal.
 */

import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, ArrowRight, Eye, EyeOff, ArrowLeft } from 'lucide-react';
import { AshokaChakra, GovEmblem } from '../components/gov/GovUI';
import GovUtilityBar from '../components/gov/GovUtilityBar';
import GovFooter from '../components/gov/GovFooter';
import { usePageTitle } from '../hooks/usePageTitle';

interface LoginPageProps {
  isModal?: boolean;
  onClose?: () => void;
}

// Quick-fill demo credentials for the login form.
// Passwords shown here are the seeded default with its first letter capitalised
// (e.g. default "pankaj56" -> "Pankaj56") — the password each account should be
// changed to via the forced change-password flow, not necessarily what is live
// in the database today. Clicking a card only fills the fields; it does not
// submit, so it never masks a real login failure.
const QUICK_LOGINS: { label: string; designation: string; username: string; password: string }[] = [
  { label: 'Admin',  designation: 'Platform Administrator',     username: 'admin',          password: 'admin123' },
  { label: 'Shikha',  designation: 'Deputy Director',            username: 'usr_720465595',  password: 'Shikha95' },
  { label: 'Pankaj',  designation: 'Junior Statistical Officer',  username: 'usr_791131756',  password: 'Pankaj56' },
];

const LoginPage: React.FC<LoginPageProps> = ({ isModal = false, onClose }) => {
  const navigate         = useNavigate();
  const location         = useLocation();
  const { login }        = useAuth();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);

  usePageTitle(
    isModal ? undefined : 'Official Login',
    'Sign in to KarmaSkill with your iGOT Karmayogi user identity.'
  );

  // Where to go after login if redirected from a protected route
  const from = (location.state as any)?.from?.pathname ?? null;

  const fillQuickLogin = (username: string, quickPassword: string) => {
    setError('');
    setUsername(username);
    setPassword(quickPassword);
    setShowPass(true);
  };

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

  const signInPanel = (
    <div className={isModal ? "fixed inset-0 z-[60] flex items-center justify-center bg-gov-ink/60 backdrop-blur-md font-sans animate-fade-in overflow-y-auto py-10" : "flex flex-1 items-center justify-center relative overflow-hidden gov-page-bg font-sans transition-colors duration-300 py-10"}>
      {/* Background */}
      {!isModal && (
        <>
          <div className="absolute inset-x-0 top-0 h-[42vh] bg-gradient-to-br from-gov-ink via-gov-navy to-gov-blue" />
          <div className="absolute inset-x-0 top-[42vh] tricolor-strip" />
          <div className="absolute -right-32 -top-32 text-white/[0.06] pointer-events-none">
            <AshokaChakra size={560} strokeWidth={0.8} className="animate-spin-slow" />
          </div>
        </>
      )}

      {isModal && <div className="absolute inset-0" onClick={onClose} aria-hidden="true" />}

      <div className="relative z-10 w-full max-w-md px-4 animate-scale-in">
        {isModal && (
          <button
            onClick={onClose}
            className="mb-4 inline-flex items-center gap-2 text-white/90 hover:text-white bg-white/10 hover:bg-white/20 border border-white/20 px-3.5 py-1.5 rounded-full text-[12px] font-bold backdrop-blur-md transition-all"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Home
          </button>
        )}

        {/* Card */}
        <div className="relative bg-white dark:bg-slate-900 rounded-2xl shadow-gov-lg border border-gov-line dark:border-slate-700/60 overflow-hidden transition-colors duration-300">
          <div className="tricolor-strip" />

          {/* Ministry block */}
          <div className="flex items-center gap-3.5 px-8 pt-7 pb-5 border-b border-gov-line dark:border-slate-800">
            <GovEmblem size={52} />
            <div className="leading-tight">
              <div className="text-[11px] font-semibold text-gov-saffron-deep" lang="hi">सांख्यिकी और कार्यक्रम कार्यान्वयन मंत्रालय</div>
              <div className="font-serif font-bold text-[14px] text-gov-ink dark:text-white">Ministry of Statistics &amp; PI</div>
              <div className="text-[9.5px] font-bold uppercase tracking-[0.2em] text-slate-400 mt-0.5">Skill Intelligence Platform</div>
            </div>
          </div>

          <div className="p-8 pt-6">
          <h2 className="font-serif text-[22px] font-bold text-gov-ink dark:text-white mb-1">Official Sign-In <span className="text-[14px] font-sans font-semibold text-slate-400" lang="hi">· अधिकारी लॉगिन</span></h2>
          <p className="text-[13px] text-slate-500 dark:text-slate-400 mb-4">Use your iGOT Karmayogi user ID to access your dashboard.</p>

          {/* Demo quick-fill credentials — fills the form only, does not submit */}
          <div className="mb-6">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wide mb-2">Quick Demo Sign-In</div>
            <div className="grid grid-cols-3 gap-2">
              {QUICK_LOGINS.map(q => (
                <button
                  key={q.username}
                  type="button"
                  onClick={() => fillQuickLogin(q.username, q.password)}
                  className="text-left px-2.5 py-2 rounded-lg border border-gov-line dark:border-slate-700 bg-slate-50 dark:bg-slate-800/60 hover:bg-gov-saffron/10 hover:border-gov-saffron transition-colors"
                  title={`${q.username} · ${q.designation}`}
                >
                  <div className="text-[12px] font-bold text-gov-ink dark:text-white truncate">{q.label}</div>
                  <div className="text-[9.5px] text-slate-400 truncate">{q.designation}</div>
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            {/* Username */}
            <div>
              <label htmlFor="login-username" className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-1.5">
                Username
              </label>
              <input
                id="login-username"
                name="username"
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
                autoFocus={isModal}
                autoComplete="username"
                aria-invalid={!!error}
                aria-describedby={error ? 'login-error' : undefined}
                placeholder="Enter your iGOT User ID or admin"
                className="gov-input"
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="login-password" className="block text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  id="login-password"
                  name="password"
                  type={showPass ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  aria-invalid={!!error}
                  aria-describedby={error ? 'login-error' : undefined}
                  placeholder="••••••••"
                  className="gov-input pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(v => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                  aria-pressed={showPass}
                  aria-label={showPass ? 'Hide password' : 'Show password'}
                >
                  {showPass ? <EyeOff className="w-4 h-4" aria-hidden="true" /> : <Eye className="w-4 h-4" aria-hidden="true" />}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <p id="login-error" role="alert" className="text-[12px] text-red-600 font-medium bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded-md px-3 py-2 animate-fade-in">
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
                <>Sign In <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </form>

          <div className="mt-5 flex items-center gap-1.5 text-[11px] text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-gov-green" />
            Secured session · Role-based access for officials and administrators
          </div>
          </div>
        </div>

        <p className={`text-center mt-6 text-[11px] ${isModal ? 'text-white/60' : 'text-slate-500'}`}>
          © {new Date().getFullYear()} Ministry of Statistics and Programme Implementation
        </p>
      </div>
    </div>
  );

  // As a modal the landing page supplies the chrome around it.
  if (isModal) return signInPanel;

  return (
    <div className="flex min-h-screen flex-col">
      <a href="#main-content" className="skip-link">Skip to main content</a>
      <GovUtilityBar mainId="main-content" />
      <div className="tricolor-strip" />
      <main id="main-content" tabIndex={-1} className="flex flex-1 flex-col">
        {signInPanel}
      </main>
      <GovFooter variant="compact" />
    </div>
  );
};

export default LoginPage;
