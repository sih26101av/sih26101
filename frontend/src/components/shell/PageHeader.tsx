/**
 * FILE: src/components/shell/PageHeader.tsx
 *
 * Title row at the top of every shell view: the breadcrumb trail, then the page
 * title + strapline on the left and the date chip / actions on the right.
 *
 * GIGW 3.0 asks interior pages to show the user where they are, so the trail
 * renders at every width (it used to appear only above 1280px) and as a real
 * `nav > ol > li` list via `components/gov/Breadcrumbs.tsx`. The `<h1>` here is
 * the one per-view top-level heading; sections below use `<h2>`.
 */

import React from 'react';
import { CalendarDays } from 'lucide-react';
import Breadcrumbs, { type Crumb } from '../gov/Breadcrumbs';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  /**
   * e.g. ["Home", "Learner", "Dashboard"] — the last entry is the current page.
   * Plain strings keep the call sites short; the first one links to the portal
   * home. Pass `Crumb` objects where a middle step needs its own link.
   */
  breadcrumb?: (string | Crumb)[];
  /** Small caption under the date, e.g. "Keep learning, keep growing!". */
  dateCaption?: string;
  /** Extra controls (buttons) rendered next to the date chip. */
  actions?: React.ReactNode;
}

const toCrumbs = (items: (string | Crumb)[]): Crumb[] =>
  items.map((item, i) =>
    typeof item === 'string' ? { label: item, to: i === 0 ? '/' : undefined } : item
  );

const PageHeader: React.FC<PageHeaderProps> = ({ title, subtitle, breadcrumb, dateCaption, actions }) => {
  const today = new Date().toLocaleDateString('en-IN', {
    weekday: 'long', day: 'numeric', month: 'short', year: 'numeric',
  });

  return (
    <div className="mb-4 sm:mb-5">
      {breadcrumb && breadcrumb.length > 0 && (
        <Breadcrumbs items={toCrumbs(breadcrumb)} className="mb-2.5" />
      )}

      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div className="min-w-0">
          <h1 className="shell-title">{title}</h1>
          {subtitle && <p className="mt-1.5 pl-3.5 text-[12.5px] sm:text-[13px] text-slate-500 dark:text-slate-400">{subtitle}</p>}
        </div>

        <div className="flex flex-shrink-0 flex-wrap items-center gap-2.5">
          {actions}
          <div className="panel hidden items-center gap-2.5 px-3.5 py-2 sm:flex print:hidden">
            <CalendarDays size={16} className="text-gov-blue dark:text-sky-400" aria-hidden="true" />
            <span className="leading-tight">
              <span className="block text-[12px] font-semibold text-gov-ink dark:text-white">{today}</span>
              {dateCaption && <span className="block text-[10.5px] text-slate-400">{dateCaption}</span>}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PageHeader;
