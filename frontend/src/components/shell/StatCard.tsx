/**
 * FILE: src/components/shell/StatCard.tsx
 *
 * KPI tile shared by the learner and admin dashboards.
 * Renders as a <button> when `onClick` is supplied, otherwise as a plain <div>,
 * so a tile is only focusable when it actually does something.
 */

import React from 'react';
import { CountUp } from '../gov/GovUI';

export type StatTone = 'blue' | 'orange' | 'green' | 'purple' | 'rose' | 'navy';

const TONES: Record<StatTone, { tile: string; icon: string }> = {
  blue:   { tile: 'bg-accent-blue-soft dark:bg-blue-500/15',     icon: 'text-accent-blue dark:text-blue-300' },
  orange: { tile: 'bg-accent-orange-soft dark:bg-orange-500/15', icon: 'text-accent-orange dark:text-orange-300' },
  green:  { tile: 'bg-accent-green-soft dark:bg-emerald-500/15', icon: 'text-accent-green dark:text-emerald-300' },
  purple: { tile: 'bg-accent-purple-soft dark:bg-violet-500/15', icon: 'text-accent-purple dark:text-violet-300' },
  rose:   { tile: 'bg-accent-rose-soft dark:bg-rose-500/15',     icon: 'text-accent-rose dark:text-rose-300' },
  navy:   { tile: 'bg-gov-navy/[0.08] dark:bg-sky-500/15',       icon: 'text-gov-navy dark:text-sky-300' },
};

interface StatCardProps {
  icon: React.ElementType;
  label: string;
  /** Numbers animate with CountUp; strings render as-is. */
  value: number | string;
  tone?: StatTone;
  /** e.g. "+12%" — rendered as a green/rose chip depending on `deltaDirection`. */
  delta?: string;
  deltaDirection?: 'up' | 'down';
  /** Small line under the value, e.g. "+1,986 this month". */
  caption?: string;
  /** Optional 0–100 progress bar under the value. */
  progress?: number;
  onClick?: () => void;
  /** Stagger index for the entrance animation. */
  index?: number;
}

const StatCard: React.FC<StatCardProps> = ({
  icon: Icon, label, value, tone = 'blue', delta, deltaDirection = 'up',
  caption, progress, onClick, index = 0,
}) => {
  const t = TONES[tone];

  const body = (
    <>
      <div className="flex items-start gap-3.5">
        <span className={`flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl transition-transform duration-300 group-hover:scale-105 ${t.tile}`}>
          <Icon size={20} className={t.icon} aria-hidden="true" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="truncate text-[12.5px] font-medium text-slate-500 dark:text-slate-400">{label}</p>
          <div className="mt-0.5 flex flex-wrap items-center gap-2">
            {typeof value === 'number' ? (
              <CountUp end={value} duration={900} className="text-[25px] font-bold leading-none tracking-tight text-gov-ink dark:text-white" />
            ) : (
              <span className="text-[25px] font-bold leading-none tracking-tight text-gov-ink dark:text-white">{value}</span>
            )}
            {delta && (
              <span
                className={`chip ${
                  deltaDirection === 'up'
                    ? 'bg-accent-green-soft text-accent-green dark:bg-emerald-500/15 dark:text-emerald-300'
                    : 'bg-accent-rose-soft text-accent-rose dark:bg-rose-500/15 dark:text-rose-300'
                }`}
              >
                {deltaDirection === 'up' ? '↑' : '↓'} {delta}
              </span>
            )}
          </div>
        </div>
      </div>

      {typeof progress === 'number' && (
        <div className="mt-3.5 h-1.5 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700/60">
          <div
            className="h-full rounded-full bg-gov-saffron transition-[width] duration-700"
            style={{ width: `${Math.max(0, Math.min(100, progress))}%` }}
          />
        </div>
      )}

      {caption && (
        <p className="mt-2.5 text-[11.5px] font-medium text-slate-400 dark:text-slate-500">{caption}</p>
      )}
    </>
  );

  const shell =
    'panel group animate-fade-up p-5 text-left transition-all duration-300 hover:-translate-y-0.5 hover:shadow-gov';
  const style = { animationDelay: `${index * 70}ms` } as React.CSSProperties;

  return onClick ? (
    <button type="button" onClick={onClick} className={`${shell} w-full hover:border-gov-blue/30`} style={style}>
      {body}
    </button>
  ) : (
    <div className={shell} style={style}>
      {body}
    </div>
  );
};

export default StatCard;
