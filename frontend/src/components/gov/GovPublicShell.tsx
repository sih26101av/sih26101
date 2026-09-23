/**
 * FILE: src/components/gov/GovPublicShell.tsx
 *
 * Chrome for the signed-out pages that are not the landing page — the statutory
 * policy pages and the 404. It carries the same masthead, utility strip and
 * footer as the rest of the portal so a user who arrives on a policy page still
 * lands on something recognisably the same site.
 *
 * The landing page keeps its own richer header; this is the plain version.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import GovUtilityBar from './GovUtilityBar';
import GovFooter from './GovFooter';
import Breadcrumbs, { type Crumb } from './Breadcrumbs';
import { GovEmblem } from './GovUI';
import { useScreenReader } from '../../hooks/useScreenReader';
import { useAccessibility } from '../../context/AccessibilityContext';
import { usePageTitle } from '../../hooks/usePageTitle';

interface GovPublicShellProps {
  title: string;
  /** Devanagari rendering of the title, shown beneath it. */
  titleHi?: string;
  subtitle?: string;
  breadcrumb?: Crumb[];
  /** Rendered at the end of the header block (e.g. a "last reviewed" line). */
  headerMeta?: React.ReactNode;
  children: React.ReactNode;
}

const GovPublicShell: React.FC<GovPublicShellProps> = ({
  title, titleHi, subtitle, breadcrumb = [], headerMeta, children,
}) => {
  const { lang } = useAccessibility();
  const screenReader = useScreenReader(lang);
  usePageTitle(title, subtitle);

  return (
    <div className="flex min-h-screen flex-col bg-gov-paper dark:bg-[#07111f]">
      <a href="#main-content" className="skip-link">Skip to main content</a>

      <GovUtilityBar mainId="main-content" screenReader={screenReader} />
      <div className="tricolor-strip" />

      {/* ── Masthead ───────────────────────────────────────────────────── */}
      <header role="banner" className="border-b border-gov-line bg-white dark:border-slate-800 dark:bg-[#0b1628]">
        <div className="mx-auto flex max-w-[1100px] items-center gap-4 px-4 py-4 md:px-6">
          <Link to="/" className="flex items-center gap-3.5" aria-label="KarmaSkill home">
            <GovEmblem size={48} className="flex-shrink-0" />
            <span className="leading-tight">
              <span className="block text-[10px] font-bold uppercase tracking-[0.13em] text-gov-blue dark:text-sky-300">
                Ministry of Statistics &amp; Programme Implementation
              </span>
              <span className="block font-serif text-[20px] font-bold text-gov-ink dark:text-white">KarmaSkill</span>
              <span className="block text-[9.5px] font-bold uppercase tracking-[0.17em] text-slate-500 dark:text-slate-400">
                Skill Intelligence Platform · Government of India
              </span>
            </span>
          </Link>
        </div>
      </header>

      {/* ── Page ───────────────────────────────────────────────────────── */}
      <main id="main-content" tabIndex={-1} className="flex-1">
        <div className="mx-auto w-full max-w-[1100px] px-4 py-6 md:px-6 md:py-9">
          {breadcrumb.length > 0 && <Breadcrumbs items={breadcrumb} className="mb-4" />}

          <div className="mb-6 border-b border-gov-line pb-5 dark:border-slate-800">
            <h1 className="gov-heading text-[26px] leading-tight md:text-[32px]">{title}</h1>
            {titleHi && (
              <p lang="hi" className="mt-1.5 pl-4 font-serif text-[16px] text-slate-500 dark:text-slate-400">{titleHi}</p>
            )}
            {subtitle && (
              <p className="mt-3 max-w-3xl pl-4 text-[14px] leading-relaxed text-slate-600 dark:text-slate-300">{subtitle}</p>
            )}
            {headerMeta && <div className="mt-3 pl-4">{headerMeta}</div>}
          </div>

          {children}
        </div>
      </main>

      <GovFooter />
    </div>
  );
};

export default GovPublicShell;
