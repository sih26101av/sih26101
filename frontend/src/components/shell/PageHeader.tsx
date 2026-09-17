/**
 * FILE: src/components/shell/PageHeader.tsx
 *
 * Title row at the top of every shell view: page title + strapline on the left,
 * breadcrumb / date chip on the right (matching the reference dashboards).
 */

import React from 'react';
import { CalendarDays, ChevronRight } from 'lucide-react';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  /** e.g. ["Home", "Learner", "Dashboard"] — the last entry is emphasised. */
  breadcrumb?: string[];
  /** Small caption under the date, e.g. "Keep learning, keep growing!". */
  dateCaption?: string;
  /** Extra controls (buttons) rendered next to the date chip. */
  actions?: React.ReactNode;
}

const PageHeader: React.FC<PageHeaderProps> = ({ title, subtitle, breadcrumb, dateCaption, actions }) => {
  const today = new Date().toLocaleDateString('en-IN', {
    weekday: 'long', day: 'numeric', month: 'short', year: 'numeric',
  });

  return (
    <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
      <div className="min-w-0">
        <h1 className="shell-title">{title}</h1>
        {subtitle && <p className="mt-1.5 pl-3.5 text-[13px] text-slate-500 dark:text-slate-400">{subtitle}</p>}
      </div>

      <div className="flex flex-shrink-0 flex-wrap items-center gap-2.5">
        {breadcrumb && breadcrumb.length > 0 && (
          <nav aria-label="Breadcrumb" className="hidden items-center gap-1 text-[11.5px] text-slate-400 xl:flex">
            {breadcrumb.map((crumb, i) => (
              <React.Fragment key={crumb + i}>
                {i > 0 && <ChevronRight size={12} aria-hidden="true" />}
                <span className={i === breadcrumb.length - 1 ? 'font-semibold text-gov-navy dark:text-slate-200' : ''}>
                  {crumb}
                </span>
              </React.Fragment>
            ))}
          </nav>
        )}
        {actions}
        <div className="panel flex items-center gap-2.5 px-3.5 py-2">
          <CalendarDays size={16} className="text-gov-blue dark:text-sky-400" aria-hidden="true" />
          <span className="leading-tight">
            <span className="block text-[12px] font-semibold text-gov-ink dark:text-white">{today}</span>
            {dateCaption && <span className="block text-[10.5px] text-slate-400">{dateCaption}</span>}
          </span>
        </div>
      </div>
    </div>
  );
};

export default PageHeader;
