/**
 * FILE: src/components/shell/AppShell.tsx
 *
 * Shared dashboard chrome for the learner and admin dashboards: the navy NSO
 * topbar, the left section navigation (drawer on mobile) and the content canvas.
 *
 * It owns *no* data — every consumer passes its own nav model and children, so
 * the learner and admin pages keep their existing state and fetch logic.
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bell, ChevronDown, LogOut, Menu, Moon, Search, Sun, X,
} from 'lucide-react';
import { useTheme } from '../../hooks/useTheme';
import { useAuth } from '../../context/AuthContext';
import { GovEmblem } from '../gov/GovUI';

export interface ShellNavItem {
  id: string;
  label: string;
  icon: React.ElementType;
  /** Optional count badge (e.g. number of open gaps). Hidden when 0/undefined. */
  badge?: number;
}

export interface ShellNavGroup {
  /** Optional small caps label above the group. */
  label?: string;
  items: ShellNavItem[];
}

interface AppShellProps {
  /** Sidebar sections. */
  groups: ShellNavGroup[];
  activeId: string;
  onNavigate: (id: string) => void;

  /** Topbar identity. */
  userName?: string;
  userRole?: string;

  /** Notification count shown on the bell; omit to hide the dot. */
  notificationCount?: number;
  /** Called when the bell is clicked. Omit to render the bell as decorative-disabled. */
  onNotificationsClick?: () => void;

  /** Search box — controlled by the consumer so each page filters its own data. */
  searchValue?: string;
  onSearchChange?: (value: string) => void;
  searchPlaceholder?: string;

  /** Rendered at the bottom of the sidebar (help card / ministry mark). */
  sidebarFooter?: React.ReactNode;
  /** Decorative illustration between the nav and the footer (desktop sidebar only). */
  sidebarArt?: React.ReactNode;

  children: React.ReactNode;
}

const AppShell: React.FC<AppShellProps> = ({
  groups,
  activeId,
  onNavigate,
  userName,
  userRole,
  notificationCount,
  onNotificationsClick,
  searchValue,
  onSearchChange,
  searchPlaceholder = 'Search…',
  sidebarFooter,
  sidebarArt,
  children,
}) => {
  const { theme, toggleTheme } = useTheme();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  // Close the mobile drawer whenever the section changes.
  useEffect(() => { setDrawerOpen(false); }, [activeId]);

  // Escape closes both overlays.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { setDrawerOpen(false); setMenuOpen(false); }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const handleSignOut = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  const initial = (userName ?? 'U').trim().charAt(0).toUpperCase();

  const navList = (
    <nav className="flex flex-1 flex-col gap-5 overflow-y-auto px-3 py-5 custom-scrollbar" aria-label="Dashboard sections">
      {groups.map((group, gi) => (
        <div key={group.label ?? gi} className="space-y-1">
          {group.label && (
            <p className="px-3 pb-1.5 text-[10.5px] font-semibold uppercase tracking-[0.14em] text-slate-400 dark:text-slate-500">
              {group.label}
            </p>
          )}
          {group.items.map(({ id, label, icon: Icon, badge }) => (
            <button
              key={id}
              type="button"
              onClick={() => onNavigate(id)}
              aria-current={activeId === id ? 'page' : undefined}
              className="shell-nav-item"
            >
              <Icon size={17} className="flex-shrink-0" aria-hidden="true" />
              <span className="flex-1 text-left">{label}</span>
              {!!badge && (
                <span className="chip bg-accent-rose-soft text-accent-rose dark:bg-rose-500/20 dark:text-rose-300">
                  {badge}
                </span>
              )}
            </button>
          ))}
        </div>
      ))}
    </nav>
  );

  return (
    <div className="min-h-screen gov-canvas transition-colors duration-300">
      {/* ── Topbar ───────────────────────────────────────────────────────── */}
      <header className="sticky top-0 z-40 shadow-gov">
        <div className="tricolor-strip" />
        <div className="flex items-center gap-3 bg-gradient-to-r from-gov-ink via-gov-navy to-gov-blue px-3 py-2.5 md:px-5">
          <button
            type="button"
            onClick={() => setDrawerOpen(true)}
            className="rounded-lg p-2 text-white transition-colors hover:bg-white/10 lg:hidden"
            aria-label="Open navigation menu"
          >
            <Menu size={19} />
          </button>

          <button
            type="button"
            onClick={() => navigate('/')}
            className="group flex items-center gap-3 text-left"
            aria-label="Go to home page"
          >
            <GovEmblem size={38} className="flex-shrink-0 transition-transform duration-500 group-hover:rotate-12" />
            <span className="leading-tight">
              <span className="block text-[10px] font-semibold text-gov-saffron" lang="hi">राष्ट्रीय सांख्यिकी कार्यालय</span>
              <span className="block text-[13px] font-semibold tracking-tight text-white md:text-[15.5px]">
                National Statistical Office (NSO) Training Portal
              </span>
              <span className="hidden text-[9px] font-semibold uppercase tracking-[0.18em] text-white/55 md:block">
                Ministry of Statistics &amp; PI · Government of India
              </span>
            </span>
          </button>

          {/* Search — only rendered when the page wires it up */}
          {onSearchChange && (
            <div className="relative mx-auto hidden max-w-md flex-1 md:block">
              <Search size={15} className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" aria-hidden="true" />
              <input
                type="search"
                value={searchValue ?? ''}
                onChange={(e) => onSearchChange(e.target.value)}
                placeholder={searchPlaceholder}
                aria-label={searchPlaceholder}
                className="w-full rounded-full border border-white/15 bg-white/95 py-2 pl-10 pr-4 text-[12.5px] text-slate-700
                  placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-gov-saffron
                  dark:bg-slate-800/95 dark:text-white"
              />
            </div>
          )}

          <div className={`flex items-center gap-1 text-white ${onSearchChange ? '' : 'ml-auto'}`}>
            <button
              type="button"
              onClick={onNotificationsClick}
              disabled={!onNotificationsClick}
              className="relative rounded-full p-2 transition-colors hover:bg-white/10 disabled:cursor-default disabled:opacity-70"
              aria-label={
                notificationCount
                  ? `Notifications, ${notificationCount} unread`
                  : 'Notifications'
              }
            >
              <Bell size={17} />
              {!!notificationCount && (
                <span className="absolute right-1 top-1 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-accent-rose px-1 text-[9px] font-bold text-white">
                  {notificationCount > 9 ? '9+' : notificationCount}
                </span>
              )}
            </button>

            <button
              type="button"
              onClick={toggleTheme}
              className="rounded-full p-2 transition-colors hover:bg-white/10"
              aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
            >
              <span
                className="block transition-transform duration-500"
                style={{ transform: theme === 'dark' ? 'rotate(180deg)' : 'none' }}
              >
                {theme === 'dark' ? <Sun size={17} /> : <Moon size={17} />}
              </span>
            </button>

            {/* Account menu */}
            <div className="relative ml-1">
              <button
                type="button"
                onClick={() => setMenuOpen((o) => !o)}
                aria-expanded={menuOpen}
                aria-haspopup="menu"
                className="flex items-center gap-2 rounded-full border border-white/20 py-1 pl-1 pr-2 transition-colors hover:bg-white/10 sm:pr-3"
              >
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-gov-saffron text-[11px] font-bold text-gov-ink">
                  {initial}
                </span>
                <span className="hidden text-left leading-tight sm:block">
                  <span className="block text-[11.5px] font-semibold">{userName ?? 'Account'}</span>
                  {userRole && <span className="block text-[9.5px] text-white/60">{userRole}</span>}
                </span>
                <ChevronDown size={14} className={`hidden transition-transform sm:block ${menuOpen ? 'rotate-180' : ''}`} />
              </button>

              {menuOpen && (
                <>
                  <div className="fixed inset-0 z-0" onClick={() => setMenuOpen(false)} aria-hidden="true" />
                  <div
                    role="menu"
                    className="animate-scale-in absolute right-0 z-10 mt-2 w-52 overflow-hidden rounded-xl border border-gov-line bg-white py-1.5 shadow-gov-lg dark:border-slate-700 dark:bg-slate-800"
                  >
                    <button
                      role="menuitem"
                      onClick={() => { setMenuOpen(false); navigate('/change-password'); }}
                      className="flex w-full items-center gap-2.5 px-4 py-2.5 text-left text-[13px] font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:text-slate-200 dark:hover:bg-slate-700/60"
                    >
                      Change password
                    </button>
                    <button
                      role="menuitem"
                      onClick={handleSignOut}
                      className="flex w-full items-center gap-2.5 px-4 py-2.5 text-left text-[13px] font-medium text-accent-rose transition-colors hover:bg-rose-50 dark:hover:bg-rose-900/20"
                    >
                      <LogOut size={14} /> Sign out
                    </button>
                  </div>
                </>
              )}
            </div>

            <button
              type="button"
              onClick={handleSignOut}
              className="ml-1 hidden items-center gap-1.5 rounded-full border border-white/40 px-3.5 py-1.5 text-[11.5px] font-semibold transition-all hover:border-gov-saffron hover:bg-gov-saffron hover:text-gov-ink lg:flex"
            >
              <LogOut size={13} /> Sign Out
            </button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* ── Sidebar (desktop) ──────────────────────────────────────────── */}
        <aside className="sticky top-[62px] hidden h-[calc(100vh-62px)] w-[246px] flex-shrink-0 flex-col border-r border-gov-line bg-white dark:border-slate-800 dark:bg-slate-900/60 lg:flex">
          {navList}
          {sidebarArt}
          {sidebarFooter && <div className="px-3 pb-4">{sidebarFooter}</div>}
        </aside>

        {/* ── Sidebar (mobile drawer) ────────────────────────────────────── */}
        {drawerOpen && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <div
              className="animate-fade-in absolute inset-0 bg-gov-ink/50 backdrop-blur-sm"
              onClick={() => setDrawerOpen(false)}
              aria-hidden="true"
            />
            <aside
              className="absolute left-0 top-0 flex h-full w-[264px] flex-col bg-white shadow-gov-lg dark:bg-slate-900"
              role="dialog"
              aria-modal="true"
              aria-label="Navigation menu"
            >
              <div className="flex items-center justify-between border-b border-gov-line px-4 py-3.5 dark:border-slate-800">
                <span className="text-[13px] font-semibold text-gov-ink dark:text-white">Menu</span>
                <button
                  type="button"
                  onClick={() => setDrawerOpen(false)}
                  className="rounded-lg p-1.5 text-slate-500 transition-colors hover:bg-slate-100 dark:hover:bg-slate-800"
                  aria-label="Close navigation menu"
                >
                  <X size={18} />
                </button>
              </div>
              {navList}
              {sidebarFooter && <div className="px-3 pb-4">{sidebarFooter}</div>}
            </aside>
          </div>
        )}

        {/* ── Content ────────────────────────────────────────────────────── */}
        <div className="flex min-w-0 flex-1 flex-col">
          <main className="flex-1 px-4 py-6 md:px-6 lg:px-7">
            <div className="mx-auto w-full max-w-[1340px]">{children}</div>
          </main>

          <footer className="mt-auto bg-gov-ink text-white/60">
            <div className="tricolor-strip" />
            <div className="mx-auto flex max-w-[1340px] flex-col items-center justify-between gap-2 px-4 py-4 text-[11.5px] sm:flex-row md:px-6">
              <span>© {new Date().getFullYear()} Ministry of Statistics &amp; Programme Implementation · Government of India</span>
              <span className="flex items-center gap-2">
                MoSPI Skill Intelligence Platform
                <span className="h-1 w-1 rounded-full bg-gov-saffron" />
                Powered by iGOT Karmayogi
              </span>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
};

export default AppShell;
