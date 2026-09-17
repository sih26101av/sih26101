/**
 * FILE: src/components/gov/GovUI.tsx
 *
 * Shared presentational primitives for the government-portal look:
 *  - AshokaChakra  : 24-spoke wheel SVG (decorative emblem / watermark)
 *  - GovEmblem     : chakra in a ringed badge, used in headers
 *  - Reveal        : fades children in when scrolled into view
 *  - CountUp       : animates a number from 0 when scrolled into view
 */

import React, { useEffect, useRef, useState } from 'react';

// ── Ashoka Chakra ────────────────────────────────────────────────────────────
export const AshokaChakra: React.FC<{ size?: number; className?: string; strokeWidth?: number }> = ({
  size = 40,
  className = '',
  strokeWidth = 1.4,
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 100 100"
    className={className}
    fill="none"
    stroke="currentColor"
    aria-hidden="true"
  >
    <circle cx="50" cy="50" r="46" strokeWidth={strokeWidth * 2.2} />
    <circle cx="50" cy="50" r="7" strokeWidth={strokeWidth * 1.6} />
    {Array.from({ length: 24 }).map((_, i) => {
      const a = (i * 15 * Math.PI) / 180;
      return (
        <line
          key={i}
          x1={50 + 7 * Math.cos(a)}
          y1={50 + 7 * Math.sin(a)}
          x2={50 + 44 * Math.cos(a)}
          y2={50 + 44 * Math.sin(a)}
          strokeWidth={strokeWidth}
        />
      );
    })}
    {Array.from({ length: 24 }).map((_, i) => {
      const a = ((i * 15 + 7.5) * Math.PI) / 180;
      return <circle key={`d${i}`} cx={50 + 46 * Math.cos(a)} cy={50 + 46 * Math.sin(a)} r="1.6" fill="currentColor" stroke="none" />;
    })}
  </svg>
);

export const GovEmblem: React.FC<{ size?: number; className?: string }> = ({ size = 48, className = '' }) => (
  <div
    className={`relative flex items-center justify-center rounded-full bg-white shadow-gov ring-2 ring-gov-saffron/70 ${className}`}
    style={{ width: size, height: size }}
  >
    <div className="absolute inset-[3px] rounded-full ring-1 ring-gov-green/40" />
    <AshokaChakra size={size * 0.72} className="text-gov-navy animate-spin-slow" />
  </div>
);

// ── Intersection helper ──────────────────────────────────────────────────────
function useInView<T extends Element>(threshold = 0.15) {
  const ref = useRef<T>(null);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (typeof IntersectionObserver === 'undefined') {
      setInView(true);
      return;
    }
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          obs.disconnect();
        }
      },
      { threshold }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);

  return { ref, inView };
}

// ── Reveal on scroll ─────────────────────────────────────────────────────────
export const Reveal: React.FC<{
  children: React.ReactNode;
  delay?: number; // ms
  className?: string;
  as?: 'div' | 'section' | 'li';
}> = ({ children, delay = 0, className = '', as = 'div' }) => {
  const { ref, inView } = useInView<HTMLDivElement>();
  const Tag = as as any;
  return (
    <Tag
      ref={ref}
      className={`reveal ${inView ? 'is-visible' : ''} ${className}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </Tag>
  );
};

// ── Count-up number ──────────────────────────────────────────────────────────
export const CountUp: React.FC<{
  end: number;
  duration?: number;
  decimals?: number;
  suffix?: string;
  prefix?: string;
  className?: string;
}> = ({ end, duration = 1400, decimals = 0, suffix = '', prefix = '', className = '' }) => {
  const { ref, inView } = useInView<HTMLSpanElement>(0.3);
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (!inView) return;
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    if (reduce) {
      setValue(end);
      return;
    }
    let raf = 0;
    const start = performance.now();
    const tick = (now: number) => {
      const p = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      setValue(end * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [inView, end, duration]);

  const formatted = value.toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  return (
    <span ref={ref} className={className}>
      {prefix}
      {formatted}
      {suffix}
    </span>
  );
};
