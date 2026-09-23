/**
 * FILE: src/pages/NotFoundPage.tsx
 *
 * GIGW 3.0 requires a helpful error page rather than a blank screen or a silent
 * redirect: it has to say what happened, keep the site chrome so the user is not
 * stranded, and offer a way onward.
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home, LogIn, Map } from 'lucide-react';
import GovPublicShell from '../components/gov/GovPublicShell';

const ONWARD = [
  { to: '/', icon: Home, label: 'Home', note: 'About the platform and how to sign in' },
  { to: '/login', icon: LogIn, label: 'Official Login', note: 'Sign in with your iGOT Karmayogi identity' },
  { to: '/policy/sitemap', icon: Map, label: 'Sitemap', note: 'Every section of this portal on one page' },
  { to: '/policy/help', icon: ChevronRight, label: 'Help', note: 'How to use the portal, step by step' },
];

const NotFoundPage: React.FC = () => {
  const { pathname } = useLocation();

  return (
    <GovPublicShell
      title="Page not found"
      titleHi="पृष्ठ नहीं मिला"
      subtitle="The page you asked for is not on this portal. It may have been moved, or the address may have been typed or copied incorrectly."
      breadcrumb={[{ label: 'Home', to: '/' }, { label: 'Page not found' }]}
    >
      <div className="max-w-3xl">
        <p className="mb-6 rounded-xl border border-gov-line bg-white px-4 py-3 text-[13px] text-slate-600 dark:border-slate-700/60 dark:bg-slate-900/60 dark:text-slate-300">
          Requested address: <code className="font-mono text-[12.5px] text-gov-navy dark:text-sky-300">{pathname}</code>
          <span className="mt-1.5 block text-[12px] text-slate-500 dark:text-slate-400">
            Error 404 — if you reached this page from a link on this portal, please report it through the{' '}
            <Link to="/policy/feedback" className="font-semibold text-gov-blue hover:underline dark:text-sky-300">feedback page</Link>.
          </span>
        </p>

        <h2 className="mb-3 text-[16px] font-semibold text-gov-ink dark:text-white">Where you can go from here</h2>
        <ul className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
          {ONWARD.map(({ to, icon: Icon, label, note }) => (
            <li key={to}>
              <Link
                to={to}
                className="group flex items-start gap-3 rounded-xl border border-gov-line bg-white px-4 py-3 transition-colors hover:border-gov-blue/40 dark:border-slate-700/60 dark:bg-slate-900/60"
              >
                <Icon size={16} className="mt-0.5 flex-shrink-0 text-gov-blue dark:text-sky-400" aria-hidden="true" />
                <span>
                  <span className="block text-[13.5px] font-semibold text-gov-navy group-hover:underline dark:text-sky-300">{label}</span>
                  <span className="mt-0.5 block text-[12px] leading-relaxed text-slate-500 dark:text-slate-400">{note}</span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </GovPublicShell>
  );
};

export default NotFoundPage;
