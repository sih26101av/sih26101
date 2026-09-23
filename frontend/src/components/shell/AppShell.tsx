/**
 * FILE: src/components/shell/AppShell.tsx
 *
 * Shared dashboard chrome for the learner and admin dashboards: the GIGW
 * utility strip, the navy NSO topbar, the left section navigation (drawer on
 * mobile), the content canvas and the statutory footer.
 *
 * It owns *no* data — every consumer passes its own nav model and children, so
 * the learner and admin pages keep their existing state and fetch logic.
 *
 * GIGW 3.0 chrome, present on every signed-in page as it is on the public ones:
 *  - "Skip to main content" as the first focusable element
 *  - `GovUtilityBar` — भारत सरकार identity, text size, contrast, language
 *  - landmark roles (banner / navigation / main / contentinfo) and one <h1>
 *    per view, supplied by `PageHeader`
 *  - `GovFooter variant="compact"` — policy links, content owner, last updated
 *
 * The utility strip scrolls away; only the navy topbar is sticky, so a working
 * screen keeps its vertical room (the sidebar offset stays at 62px).
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bell, ChevronDown, LogOut, Menu, Moon, Search, Sun, X,
} from 'lucide-react';
import { useTheme } from '../../hooks/useTheme';
import { useAuth } from '../../context/AuthContext';
import { GovEmblem } from '../gov/GovUI';
import GovUtilityBar from '../gov/GovUtilityBar';
import GovFooter from '../gov/GovFooter';

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
  // Phones/tablets: the topbar has no room for the search box, so it drops
  // into its own row under the bar when the search icon is tapped.
  const [mobileSearchOpen, setMobileSearchOpen] = useState(false);

  // Close the mobile drawer whenever the section changes.
  useEffect(() => { setDrawerOpen(false); }, [activeId]);

  // Escape closes both overlays.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { setDrawerOpen(false); setMenuOpen(false); setMobileSearchOpen(false); }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const handleSignOut = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  // Lock page scroll behind the open drawer (otherwise the page scrolls under a finger).
  useEffect(() => {
    if (!drawerOpen) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = prev; };
  }, [drawerOpen]);

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
              onClick={() => { setDrawerOpen(false); onNavigate(id); }}
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
      <a href="#main-content" className="skip-link">Skip to main content</a>

      {/* ── GoI utility strip (identity + accessibility controls) ────────── */}
      <GovUtilityBar mainId="main-content" showTheme={false} />

      {/* ── Topbar ───────────────────────────────────────────────────────── */}
      <header role="banner" className="sticky top-0 z-40 shadow-gov">
        <div className="tricolor-strip" />
        <div className="flex items-center gap-2 bg-gradient-to-r from-gov-ink via-gov-navy to-gov-blue px-2 py-2 sm:gap-3 sm:px-3 sm:py-2.5 md:px-5">
          <button
            type="button"
            onClick={() => setDrawerOpen(true)}
            className="flex-shrink-0 rounded-lg p-2 text-white transition-colors hover:bg-white/10 lg:hidden"
            aria-label="Open navigation menu"
          >
            <Menu size={19} />
          </button>

          <button
            type="button"
            onClick={() => navigate('/')}
            className="group flex min-w-0 items-center gap-2 text-left sm:gap-3"
            aria-label="Go to home page"
          >
            <GovEmblem size={34} className="flex-shrink-0 transition-transform duration-500 group-hover:rotate-12" />
            <span className="min-w-0 leading-tight">
              <span className="block truncate text-[10px] font-semibold text-gov-saffron" lang="hi">राष्ट्रीय सांख्यिकी कार्यालय</span>
              <span className="block truncate text-[13px] font-semibold tracking-tight text-white md:text-[15.5px]">
                <span className="sm:hidden">NSO Training Portal</span>
                <span className="hidden sm:inline">National Statistical Office (NSO) Training Portal</span>
              </span>
              <span className="hidden truncate text-[9px] font-semibold uppercase tracking-[0.18em] text-white/55 md:block">
                Ministry of Statistics &amp; PI · Government of India
              </span>
            </span>
          </button>

          {/* Search — only rendered when the page wires it up */}
          {onSearchChange && (
            <div className="relative mx-auto hidden max-w-md flex-1 lg:block">
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

          <div className={`ml-auto flex flex-shrink-0 items-center gap-0.5 text-white sm:gap-1 ${onSearchChange ? 'lg:ml-0' : ''}`}>
            {onSearchChange && (
              <button
                type="button"
                onClick={() => setMobileSearchOpen((o) => !o)}
                aria-expanded={mobileSearchOpen}
                className="rounded-full p-2 transition-colors hover:bg-white/10 lg:hidden"
                aria-label={mobileSearchOpen ? 'Close search' : 'Open search'}
              >
                {mobileSearchOpen ? <X size={17} /> : <Search size={17} />}
              </button>
            )}
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
              className="hidden rounded-full p-2 transition-colors hover:bg-white/10 sm:block"
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
                    {userName && (
                      <div className="border-b border-gov-line px-4 pb-2.5 pt-1.5 sm:hidden dark:border-slate-700">
                        <p className="truncate text-[13px] font-semibold text-gov-ink dark:text-white">{userName}</p>
                        {userRole && <p className="truncate text-[11px] text-slate-500 dark:text-slate-400">{userRole}</p>}
                      </div>
                    )}
                    <button
                      role="menuitem"
                      onClick={() => { setMenuOpen(false); toggleTheme(); }}
                      className="flex w-full items-center gap-2.5 px-4 py-2.5 text-left text-[13px] font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:text-slate-200 dark:hover:bg-slate-700/60 sm:hidden"
                    >
                      {theme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
                      {theme === 'dark' ? 'Light theme' : 'Dark theme'}
                    </button>
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
        {onSearchChange && mobileSearchOpen && (
          <div className="animate-fade-in bg-gov-navy px-3 pb-2.5 pt-1 lg:hidden">
            <div className="relative">
              <Search size={15} className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" aria-hidden="true" />
              <input
                type="search"
                autoFocus
                value={searchValue ?? ''}
                onChange={(e) => onSearchChange(e.target.value)}
                placeholder={searchPlaceholder}
                aria-label={searchPlaceholder}
                className="w-full rounded-full border border-white/15 bg-white py-2.5 pl-10 pr-4 text-[16px] text-slate-700
                  placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-gov-saffron
                  dark:bg-slate-800 dark:text-white sm:text-[13px]"
              />
            </div>
          </div>
        )}
      </header>

      <div className="flex">
        {/* ── Sidebar (desktop) ──────────────────────────────────────────── */}
        <aside
          aria-label="Section navigation"
          className="shell-sidebar-h sticky top-[62px] hidden w-[246px] flex-shrink-0 flex-col border-r border-gov-line bg-white dark:border-slate-800 dark:bg-slate-900/60 lg:flex print:hidden"
        >
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
              className="animate-drawer-in absolute left-0 top-0 flex h-full w-[82vw] max-w-[300px] flex-col bg-white shadow-gov-lg dark:bg-slate-900"
              role="dialog"
              aria-modal="true"
              aria-label="Navigation menu"
            >
              <div className="flex items-center justify-between border-b border-gov-line px-4 py-3.5 dark:border-slate-800">
                <span className="flex min-w-0 items-center gap-2.5">
                  <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gov-saffron text-[12px] font-bold text-gov-ink">
                    {initial}
                  </span>
                  <span className="min-w-0 leading-tight">
                    <span className="block truncate text-[13px] font-semibold text-gov-ink dark:text-white">{userName ?? 'Menu'}</span>
                    {userRole && <span className="block truncate text-[11px] text-slate-500 dark:text-slate-400">{userRole}</span>}
                  </span>
                </span>
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
              {sidebarFooter && <div className="px-3 pb-3">{sidebarFooter}</div>}
              <div className="border-t border-gov-line px-3 py-3 dark:border-slate-800">
                <button
                  type="button"
                  onClick={handleSignOut}
                  className="flex w-full items-center justify-center gap-2 rounded-xl border border-accent-rose/30 px-3 py-2.5 text-[13px] font-semibold text-accent-rose transition-colors hover:bg-rose-50 dark:hover:bg-rose-900/20"
                >
                  <LogOut size={15} /> Sign out
                </button>
              </div>
            </aside>
          </div>
        )}

        {/* ── Content ────────────────────────────────────────────────────── */}
        <div className="flex min-w-0 flex-1 flex-col">
          <main id="main-content" tabIndex={-1} className="shell-main flex-1 px-3 py-4 sm:px-4 sm:py-6 md:px-6 lg:px-7">
            <div className="mx-auto w-full max-w-[1340px]">{children}</div>
          </main>

          <GovFooter variant="compact" />
        </div>
      </div>
    </div>
  );
};

export default AppShell;
