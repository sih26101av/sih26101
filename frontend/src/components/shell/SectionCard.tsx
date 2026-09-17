/**
 * FILE: src/components/shell/SectionCard.tsx
 *
 * A titled panel: heading + optional subtitle on the left, an action slot on the
 * right (a "View all →" link, a filter dropdown, a count chip …), then children.
 */

import React from 'react';

interface SectionCardProps {
  title: string;
  subtitle?: string;
  /** Right-hand slot in the header row. */
  action?: React.ReactNode;
  /** Set false when the child renders its own edge-to-edge content (e.g. a table). */
  padded?: boolean;
  className?: string;
  bodyClassName?: string;
  children: React.ReactNode;
}

const SectionCard: React.FC<SectionCardProps> = ({
  title, subtitle, action, padded = true, className = '', bodyClassName = '', children,
}) => (
  <section className={`panel ${className}`}>
    <div className="panel-head">
      <div className="min-w-0">
        <h2 className="panel-title">{title}</h2>
        {subtitle && (
          <p className="mt-1 pl-3 text-[12px] text-slate-500 dark:text-slate-400">{subtitle}</p>
        )}
      </div>
      {action && <div className="flex flex-shrink-0 items-center gap-2">{action}</div>}
    </div>
    <div className={`${padded ? 'px-5 pb-5' : 'pb-0'} ${bodyClassName}`}>{children}</div>
  </section>
);

/** "View all →" style link used in section headers. */
export const SectionAction: React.FC<{ label: string; onClick: () => void }> = ({ label, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    className="group inline-flex items-center gap-1.5 rounded-lg px-2 py-1 text-[12.5px] font-semibold text-gov-blue transition-colors hover:text-gov-navy dark:text-sky-400 dark:hover:text-sky-300"
  >
    {label}
    <span className="transition-transform duration-300 group-hover:translate-x-0.5" aria-hidden="true">→</span>
  </button>
);

export default SectionCard;
