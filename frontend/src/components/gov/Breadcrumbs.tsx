/**
 * FILE: src/components/gov/Breadcrumbs.tsx
 *
 * GIGW 3.0 asks every interior page to show the user where they are in the site
 * hierarchy. This renders that trail as a real `nav > ol > li` list (so assistive
 * technology announces it as a list and reports the position), marks the current
 * page with `aria-current`, and links every earlier step.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

export interface Crumb {
  label: string;
  /** Omit on the last crumb — the page the user is already on. */
  to?: string;
}

const Breadcrumbs: React.FC<{ items: Crumb[]; className?: string }> = ({ items, className = '' }) => {
  if (items.length === 0) return null;

  return (
    <nav aria-label="Breadcrumb" className={`print:hidden ${className}`}>
      <ol className="flex flex-wrap items-center gap-1 text-[11.5px] text-slate-500 dark:text-slate-400">
        {items.map((crumb, i) => {
          const isLast = i === items.length - 1;
          return (
            <li key={`${crumb.label}-${i}`} className="flex items-center gap-1">
              {i > 0 && <ChevronRight size={12} aria-hidden="true" className="opacity-60" />}
              {crumb.to && !isLast ? (
                <Link to={crumb.to} className="rounded hover:text-gov-navy hover:underline dark:hover:text-white">
                  {crumb.label}
                </Link>
              ) : (
                <span aria-current={isLast ? 'page' : undefined} className={isLast ? 'font-semibold text-gov-navy dark:text-slate-200' : ''}>
                  {crumb.label}
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumbs;
